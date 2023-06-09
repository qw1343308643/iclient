import hashlib
import mmap
import os
import platform
import random
import socket
import struct
import subprocess
import sys
import threading
import time
import traceback
from multiprocessing import shared_memory
try:
    from multiprocessing.resource_tracker import unregister
except:
    pass

from cmpCommand.cmd.cmpPackCmd import CmpPacketCmd
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand.expand.log.logDecoretor import log_all_methods
from cmpServerHandle.cmpHandleFactory import HandleFactory
from cmpCommand.cmd.cmpdata import CMP_INFO_SHARE, CMP_DEVICE_STATUS, CMPHeader
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE


class CCMPClientProxy():
    def __init__(self):
        self.CMPClient = None
        self.client_list = []
        self.serverFlag = True
        self.toolID = None
        self.workCfg = None
        # dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
        # sys.stdout = LoggerPrint(os.path.join(dirname, "cmpLiLog"))

    def Init(self, CMPClient=None, path=None):
        """
        工具运行入口
        :param CMPClient: 回调类 详情回调函数查看cmp.py
        :param path: 工具运行的绝对路径
        :return: bool
        """
        share_name = self.getShareName(path)
        share_cls = self.getShareInfo(share_name)
        if share_cls:
            self.CMPClient = CMPClient
            self.updateShareInfo(share_cls, share_name)
            self.run(share_cls)
            return True
        else:
            return False

    # 获取共享内存名称
    def getShareName(self, path):
        path = path.replace("\\", "/")
        share_name = hashlib.md5(path.encode('utf-8')).hexdigest().upper()
        return share_name

    def windowsShareInfo(self, share_name):
        self.mmap_share = mmap.mmap(-1, 1024, access=mmap.ACCESS_WRITE, tagname=share_name)
        cnt = self.mmap_share.read_byte()
        if cnt == 0:
            return None
        else:
            self.mmap_share.seek(0)
            info_str = self.mmap_share.read(268)
            share_cls = CMP_INFO_SHARE.parse(info_str)
            return share_cls

    def linuxShareInfo(self, share_name):
        try:
            shm_a = shared_memory.SharedMemory(name=share_name, create=False, size=268)
            info_str = shm_a.buf.tobytes()
            shm_a.close()
            try:
                unregister("/" + shm_a.name, 'shared_memory')
            except:
                pass
            share_cls = CMP_INFO_SHARE.parse(info_str)
            return share_cls
        except Exception as e:
            print("cmpp get linuxShareInfo:",e)
            return None

    def mtkShareInfo(self,share_name):
        sharePath = "/data/tmp/boost_interprocess"
        path = os.path.join(sharePath, share_name)
        _fd = os.open(path, os.O_RDWR, mode=0o600)
        size = 268
        info_str = os.read(_fd, size)
        share_cls = CMP_INFO_SHARE.parse(info_str)
        return share_cls

    # 获取共享内存信息
    def getShareInfo(self, share_name):
        if platform.system().lower() == "windows":
            return self.windowsShareInfo(share_name)
        elif platform.system().lower() == "linux":
            cmd = "cat /etc/version"
            ret = subprocess.run(cmd, shell=True, capture_output=True)
            try:
                message = ret.stdout.decode().lower()
            except:
                message = ""
            if "MTK" in message or "mtk" in message:
                return self.mtkShareInfo(share_name)
            return self.linuxShareInfo(share_name)



    # 修改共享内存内容
    def updateShareInfo(self, share_cls, share_name):
        share_cls.dwPortNumber = self.CMPClient.CMPGetCustomInfo(1)  # 获取工具支持的最大并行数量
        print("updateShareInfo share_cls.dwPortNumber:", share_cls.dwPortNumber)
        value = share_cls.getbytes()
        if platform.system().lower() == "windows":
            self.mmap_share = mmap.mmap(0, len(value), access=mmap.ACCESS_WRITE, tagname=share_name)
            self.mmap_share.write(value)
        elif platform.system().lower() == "linux":
            cmd = "cat /etc/version"
            ret = subprocess.run(cmd, shell=True, capture_output=True)
            try:
                message = ret.stdout.decode().lower()
            except:
                message = ""
            if "MTK" in message or "mtk" in message:
                sharePath = "/data/tmp/boost_interprocess"
                path = os.path.join(sharePath, share_name)
                _fd = os.open(path, flags=os.O_RDWR, mode=0o600)
                size = 268
                os.write(_fd, value)
                os.ftruncate(_fd, size)
                os.close(_fd)
                return
            shm_a = shared_memory.SharedMemory(name=share_name, create=False, size=268)
            shm_a.buf[:] = value
            print("update share value:", value)
            print("share.buff:",shm_a.buf)
            shm_a.close()
            try:
                unregister("/" + shm_a.name, "shared_memory")
            except:
                pass

    # 开启工具Server端
    def createServer(self,tcp_server_socket):
        while self.serverFlag:
            try:
                client_socket, client_addr = tcp_server_socket.accept()
                print("connect success")
                client_cls = ClientManage(client_socket, self.CMPClient, self.toolID, self.workCfg)
                threading_app = threading.Thread(target=client_cls.onMessage)
                threading_app.start()
                self.client_list.append(threading_app)
                self.clientSocket = client_socket
            except OSError as e:
                return
            except Exception as e:
                return

    # 重启
    def NotifyReboot(self, clean):
        cmpHeader = CMPHeader(None)
        cmpHeader.cmd = CMP_CMD_TYPE.CMP_REBOOT_NOTIFY.value
        cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
        data = struct.pack(f"?", clean)
        cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
        value = cmpHeader.getBytes() + data
        self.clientSocket.send(value)

    def GetClientContext(self):
        return self

    def GetFlowName(self):
        return ""

    def GetCurrentStepIndex(self):
        return ""

    def GetCurrentToolIndex(self):
        return ""

    def GetToolName(self, currnetStepIndex, currnetToolIndex):
        return currnetStepIndex, currnetToolIndex

    def monitorClient(self, tcp_server_socket):
        timeCount = 0
        while 1:
            if timeCount > 30 and self.client_list == []:
                self.serverFlag = False
                tcp_server_socket.close()
                return
            for thread in self.client_list:
                if not thread.is_alive():
                    self.client_list.remove(thread)
            time.sleep(10)
            timeCount += 10

    def run(self, share_cls):
        print(f"cmpServer NetPost:{share_cls.wNetPort}")
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server_socket.bind(('127.0.0.1', share_cls.wNetPort))
        tcp_server_socket.listen(10)
        serverManage = threading.Thread(target=self.createServer, args=(tcp_server_socket, ))
        serverManage.start()
        monitorManage = threading.Thread(target=self.monitorClient, args=(tcp_server_socket,))
        monitorManage.start()


class ClientManage:
    def __init__(self, client_socket, CMPClient, toolID, workCfg):
        self.client_socket = client_socket
        self.CMPClient = CMPClient
        self.toolID = toolID
        self.workCfg = workCfg
        self.cmpServerHandle_factory = HandleFactory()
        self.runFlag = True
        self.deviceStatus = CMP_DEVICE_STATUS()
        self.refreshInterval = random.randint(600, 900)

    def onMessage(self):
        try:
            while self.runFlag:
                message = self.client_socket.recv(4096)
                if len(message) > 0:
                    process = self.cmpServerHandle_factory.getHandle(self)
                    if isinstance(message, str):
                        pass
                    elif isinstance(message, bytes):
                        cmd = CmpPacketCmd.parse(message)
                        packet_event = CmpEventPacketBinary("packet", cmd)
                        process.handle(packet_event)
        except Exception as e:
            print(f"tool onMessage:{traceback.format_exc()}")
        # self.client_socket.close()

    def sendMessage(self, message):
        print(f"tool send message:{message}")
        if isinstance(message, str):
            self.client_socket.send(message.encode(encoding='utf-8'))
        elif isinstance(message, bytes):
            self.client_socket.send(message)
        # time.sleep(1)

#
# if __name__ == '__main__':
#     # class A:
#     #     def __init__(self):
#     #         self.wNetPort = 8001
#     # a = A()
#     app = CCMPClientProxy()
#     app.Init(path=r"D:\python-cli\nettestclient_python\temp\tmp\cdm6 V1.983074AF2E053A1100BC086F15FCFAD2F\cdm\main.exe")
    # app.create_server(a)
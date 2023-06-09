import hashlib
import mmap
import os
import platform
import random
import socket
import subprocess
import threading
import time
import traceback
from multiprocessing import shared_memory
from cmpCommand.cmd.cmpPackCmd import CmpPacketCmd
from cmpCommand.cmd.cmpdata import CMP_INFO_SHARE, CMPHeader, CMP_DEVICE_STATUS
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpClientHandle.cmpClientHandleFactory import ClientHandleFactory
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE, PACKET_TYPE
from config.errorCode import NetTestClientError, ERROR_CODE_ERROR
try:
    from multiprocessing.resource_tracker import unregister
except:
    pass


class CMPClientWork:
    def __init__(self, tool, cmd_pipe, onSetStatus, onSetDeviceLog, updateNotifyLostWorkConfig, DeviceStatus, PORT, workConfigMessage, runThreads,
                 python_exe):
        self.tool = tool  # 任务信息
        self.mmap_share = None  # 共享操作句柄
        self.share_cls = None  # 共享内容
        self.tcp_client = None  # cmp客户端
        self.cmd_pipe = cmd_pipe  # 命令队列

        self.onSetStatus = onSetStatus# 回调函数,用以发送工具端的测试状态上传到服务器
        self.onSetDeviceLog = onSetDeviceLog  # 回调函数,用以发送工具端的log上传到服务器
        self.updateNotifyLostWorkConfig = updateNotifyLostWorkConfig  # 回调函数，用以正常重启前保存测试状态
        self.DeviceStatus = DeviceStatus
        self._PORT = PORT
        self.pid = []
        self.workConfigMessage = workConfigMessage
        self.runThreads = runThreads
        self.fisrtConnect = True
        self.python_exe = python_exe

        self.runFlag = True  # 运行标志位
        self.cmpClientHandle_factory = ClientHandleFactory()
        self.refreshInterval = random.randint(30, 60)
        self._doneEvent = threading.Event()

    def startTest(self):
        print("run getShareInfo")
        isRun = self.getShareInfo()
        print("isRun:", isRun)
        self.setClientParam()
        print("run setClientParam")
        if isRun:
            self.create_tool_process(self.tool.workParam["Tool"])

        return self.connectTool()


    def getShareName(self):
        """
        根据工具地址生成共享内存名称
        :return: 共享名称
        """
        share_cnt = self.runThreads.get(self.tool.workParam["MD5"])
        print("get share_cnt:",share_cnt)
        if share_cnt:
            self.share_cnt = share_cnt
            share_name = self.share_cnt.share_name
            if platform.system().lower() == "linux":
                try:
                    shm_a = shared_memory.SharedMemory(name=share_name, create=False, size=268)
                    info_str = shm_a.buf.tobytes()
                    self.share_cls = CMP_INFO_SHARE.parse(info_str)
                    shm_a.close()
                    try:
                        unregister("/" + shm_a.name, "shared_memory")
                    except:
                        pass
                    print("dwPortNumber:",self.share_cls.dwPortNumber)
                    print("current_connect:",self.share_cnt.current_connect)
                    if self.share_cls.dwPortNumber > 1 and self.share_cnt.current_connect < self.share_cls.dwPortNumber:
                        return share_name
                except:
                    pass
        self.share_cnt = ShareConnect()
        tool_path = self.tool.workParam["Tool"]
        share_name = hashlib.md5(tool_path.encode('utf-8')).hexdigest().upper()
        return share_name

    def windowsShareInfo(self):
        self.mmap_share = mmap.mmap(-1, 1024, access=mmap.ACCESS_WRITE, tagname=self.share_name)
        # 读取有效比特数，不包括空比特
        cnt = self.mmap_share.read_byte()
        if cnt == 0:
            wNetPort = self._PORT
            dwPortNumber = 1
            strLogDir = self.tool.workParam["LogDir"]
            self.share_cls = CMP_INFO_SHARE(wNetPort, dwPortNumber, strLogDir)
            value = self.share_cls.getbytes()
            self.mmap_share = mmap.mmap(0, len(value), access=mmap.ACCESS_WRITE, tagname=self.share_name)
            self.mmap_share.write(value)
            return True
        else:
            self.share_cls = self.readShareInfo()
            if self.share_cls.dwPortNumber > 1:
                share_cnt = self.runThreads[self.tool.workParam["MD5"]]
                self.runThreads[self.tool.workParam["MD5"]] = share_cnt
                return False
            self.share_cls.wNetPort = self._PORT
            value = self.share_cls.getbytes()
            self.mmap_share.seek(0)
            self.mmap_share = mmap.mmap(0, len(value), access=mmap.ACCESS_WRITE, tagname=self.share_name)
            self.mmap_share.write(value)
            return True

    def linuxShareInfo(self):
        try:
            shm_a = shared_memory.SharedMemory(name=self.share_name, create=False, size=268)
            info_str = shm_a.buf.tobytes()
            self.share_cls = CMP_INFO_SHARE.parse(info_str)
            if self.share_cls.dwPortNumber > 1:
                share_cnt = self.runThreads[self.tool.workParam["MD5"]]
                self.runThreads[self.tool.workParam["MD5"]] = share_cnt
                return False
            wNetPort = self._PORT
            dwPortNumber = 1
            strLogDir = self.tool.workParam["LogDir"]
            print(f"update share:PORT:{wNetPort}, index:{self.workConfigMessage.disk_message.index}")
            self.share_cls = CMP_INFO_SHARE(wNetPort, dwPortNumber, strLogDir)
            value = self.share_cls.getbytes()
            shm_a.buf[:] = value
            shm_a.close()
            try:
                unregister("/" + shm_a.name, "shared_memory")
            except:
                pass
            return True
        except Exception as e:
            shm_a = shared_memory.SharedMemory(name=self.share_name, create=True, size=268)
            wNetPort = self._PORT
            dwPortNumber = 1
            strLogDir = self.tool.workParam["LogDir"]
            print(f"update share:PORT:{wNetPort}, index:{self.workConfigMessage.disk_message.index}")
            self.share_cls = CMP_INFO_SHARE(wNetPort, dwPortNumber, strLogDir)
            value = self.share_cls.getbytes()
            shm_a.buf[:] = value
            shm_a.close()
            try:
                unregister("/" + shm_a.name, "shared_memory")
            except:
                pass
            return True

    def mtkShareInfo(self):
        sharePath = "/data/tmp/boost_interprocess"
        if not os.path.exists(sharePath):
            os.makedirs(sharePath)
        try:
            wNetPort = self._PORT
            dwPortNumber = 1
            strLogDir = self.tool.workParam["LogDir"]
            self.share_cls = CMP_INFO_SHARE(wNetPort, dwPortNumber, strLogDir)
            value = self.share_cls.getbytes()
            path = os.path.join(sharePath, self.share_name)
            _O_CREX = os.O_CREAT | os.O_EXCL
            _fd = os.open(path, flags=_O_CREX | os.O_RDWR, mode=0o600)
            size = 268
            os.write(_fd, value)
            os.ftruncate(_fd, size)
            os.close(_fd)
            return True
        except Exception as e:
            path = os.path.join(sharePath, self.share_name)
            _fd = os.open(path, os.O_RDWR, mode=0o600)
            size = 268
            info_str = os.read(_fd, size)
            os.close(_fd)
            self.share_cls = CMP_INFO_SHARE.parse(info_str)
            if self.share_cls.dwPortNumber > 1:
                share_cnt = self.runThreads[self.tool.workParam["MD5"]]
                self.runThreads[self.tool.workParam["MD5"]] = share_cnt
                return False
            wNetPort = self._PORT
            dwPortNumber = 1
            strLogDir = self.tool.workParam["LogDir"]
            self.share_cls = CMP_INFO_SHARE(wNetPort, dwPortNumber, strLogDir)
            value = self.share_cls.getbytes()
            _fd = os.open(path, flags=os.O_RDWR, mode=0o600)
            size = 268
            os.write(_fd, value)
            os.ftruncate(_fd, size)
            os.close(_fd)
            return True

    def getShareInfo(self):
        self.share_name = self.getShareName()
        print("share name:", self.share_name)
        if platform.system().lower() == "windows":
            return self.windowsShareInfo()
        elif platform.system().lower() == "linux":
            if os.path.exists("/etc/version"):
                cmd = "cat /etc/version"
                ret = subprocess.run(cmd, shell=True, capture_output=True)
                try:
                    message = ret.stdout.decode().lower()
                    if "MTK" in message or "mtk" in message:
                        return self.mtkShareInfo()
                except:
                    pass
            return self.linuxShareInfo()


    def readShareInfo(self):
        self.mmap_share.seek(0)
        # 把二进制转换为字符串
        info_str = self.mmap_share.read(268)
        share_cls = CMP_INFO_SHARE.parse(info_str)
        return share_cls

    def setClientParam(self):
        self.ip = "127.0.0.1"
        self.port = self.share_cls.wNetPort
        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connectTool(self):
        time_count = 0
        while 1:
            try:
                if time_count >= 120:
                    raise NetTestClientError(ERROR_CODE_ERROR.CONNECT_TOOL_FAIL.value)
                print("connect ip:",self.ip)
                print("connect port:",self.port)
                self.tcp_client.connect((self.ip, self.port))
                self.tcp_client.setblocking(False)
                self.share_cnt.share_name = self.share_name
                self.share_cnt.current_connect += 1
                self.share_cnt.current_run += 1
                self.share_cnt.port = self._PORT
                self.runThreads[self.tool.workParam["MD5"]] = self.share_cnt
                return {"result": True, "message": "Success Connect Tool"}
            except NetTestClientError:
                print("无法连接到工具端")

                return {"result": False, "message": "Connect Tool Server Fail"}
            except ConnectionRefusedError as e:
                print(f"{self.ip}:{self.port} {self.workConfigMessage.disk_message.index} {str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))}:{e}")
                # random_time = random.randint(10, 15)
                time.sleep(1)
                time_count += 1
            except Exception as e:
                print("connect Tool error:", e)

    # 发送消息
    def sendMessage(self, message):
        print(f"device:{self.tool.workParam['Device']} index:{self.tool.workParam['Index']},send message:{message}")
        try:
            if isinstance(message, str):
                self.tcp_client.send(message.encode(encoding='utf-8'))
            elif isinstance(message, bytes):
                self.tcp_client.send(message)
        except Exception as e:
            print("not connect runflag:",e)
            self.runFlag = False

     # 控制客户端的发送,监听命令队列,将数据发送给工具端
    def sendManage(self):
        while self.runFlag:
            if not self.cmd_pipe.empty():
                data = self.cmd_pipe.get()
                print(f"send:{data}")
                process = self.cmpClientHandle_factory.getHandle(self)
                cmd = CmpPacketCmd.parseCmd(data)
                packet_event = CmpEventPacketBinary("packet", cmd)
                process.handle(packet_event)
            # time.sleep(1)


    # 控制客户端的接受,获取工具端的数据
    def recvManage(self):
        while self.runFlag:
            try:
                data, addr = self.tcp_client.recvfrom(4096)
                if data == b'':
                    # self.cmd_pipe.put(
                    #     (CMP_CMD_TYPE.CMP_EXIT.value, 0, PACKET_TYPE.PACKET_NOMAL.value, ACK_TYPE.NEED_NONE.value))
                    # time.sleep(15)
                    print("tool exit")
                    break
                if data:
                    process = self.cmpClientHandle_factory.getHandle(self)
                    if isinstance(data, str):
                        pass
                    elif isinstance(data, bytes):
                        cmd = CmpPacketCmd.parse(data)
                        packet_event = CmpEventPacketBinary("packet", cmd)
                        process.handle(packet_event)
                        count = 0
                        while cmd.length < len(data):
                            data = data[cmd.length:]
                            cmd = CmpPacketCmd.parse(data)
                            packet_event = CmpEventPacketBinary("packet", cmd)
                            process.handle(packet_event)
                            count += 1
                            if count >= 3:
                                break
            except BlockingIOError as e:
                pass
            except ConnectionResetError as e:
                print(f"连接断开:{e}")
                time.sleep(10)
            except OSError as e:
                print("server disConnect:",e)
            except Exception as e:
                print(f"recv err:{traceback.format_exc()}")
        self._doneEvent.set()
        self.runFlag = False

    # 服务端需要刷新测试内容定时器
    def refreshTestStatusTimer(self):
        timeCount = 0
        while self.runFlag or self._doneEvent.is_set():
            if timeCount >= self.refreshInterval:
                self.cmd_pipe.put(
                    (CMP_CMD_TYPE.CMP_GET_STATUS.value, 0, 0, ACK_TYPE.NEED_RESPONSE.value))
                timeCount = 0
            time.sleep(1)
            timeCount += 1

    # def updateStatus(self):
    #     cmpHeader = CMPHeader(None)
    #     cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_STATUS.value
    #     cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
    #     nItem = self.tool.workParam["Index"]
    #     data = int.to_bytes(nItem, 4, "little", signed=False)
    #     cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
    #     value = cmpHeader.getBytes() + data
    #     if len(value) % 4 != 0:  # 确保4字节对齐
    #         value += bytes(4 - len(value) % 4)
    #     self.sendMessage(value)
    #     data, addr = self.tcp_client.recvfrom(4096)
    #     if data:
    #         cmd = CmpPacketCmd.parse(data)
    #         if cmd.cmd == CMP_CMD_TYPE.CMP_GET_STATUS.value:
    #             deviceStatus = CMP_DEVICE_STATUS.parse(cmd.data)
    #             status = self.DeviceStatus.parse(deviceStatus)
    #             status_id = self.tool.workParam.get("StatusID")
    #             if not status_id:
    #                 status.tool_id
    #             self.onSetStatus(self.tool.workParam["Device"], self.tool.workParam["Index"], status)


    def _end(self):
        if not self.tool.isReboot:
            print("close cmpClientWork")
            path = "lostWorkConfig.pickle"
            if os.path.exists(path):
                os.remove(path)
        path = os.path.join("/data/tmp/boost_interprocess", self.share_name)
        if os.path.exists(path):
            os.remove(path)

    # 运行
    def run(self):
        print(f"run thread index:{self.workConfigMessage.disk_message.index}, port:{self.port}")
        sendManage = threading.Thread(target=self.sendManage)  # 发送
        recvManage = threading.Thread(target=self.recvManage)  # 接收
        # refreshTestStatusTimer = threading.Thread(target=self.refreshTestStatusTimer)  # 定时刷新
        sendManage.start()
        recvManage.start()
        # refreshTestStatusTimer.start()
        self.cmd_pipe.put((CMP_CMD_TYPE.CMP_INIT.value, 0, 0, ACK_TYPE.NEED_RESPONSE.value))
        self._doneEvent.wait()
        try:
            self.runThreads.pop(self.tool.workParam["MD5"])
            self.clearUp()
        except:
            pass
        self._end()

    def create_tool_process(self, path):
        # 1. 判断系统
        # 2. 判断执行方式
        env = self.setEnviron()
        print("env:",env)
        if platform.system().lower() == "windows":
            import win32api
            win32api.ShellExecute(0, "open",
                                  path, None,
                                  os.path.dirname(path), True)
        elif platform.system().lower() == "linux":
            if path.split(".")[-1] == "py":
                cmd = f'{self.python_exe} "{path}"'
                print(cmd)
                print(f"index:{self.workConfigMessage.disk_message.index}, port:{self.port}")
                pro = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, env=env, cwd=os.path.dirname(path))
                self.pid.append(pro.pid)
            else:
                cmd = f'"{path}"'
                print("cmd:", cmd)
                pro = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, env=env, cwd=os.path.dirname(path))
                self.pid.append(pro.pid)
        else:
            pass
        return

    def setEnviron(self):
        new_env = dict(os.environ)
        if self.workConfigMessage.EnvVariables:
            for item in self.workConfigMessage.EnvVariables:
                if item.get("Key") and item.get("Value"):
                    new_env[item["Key"]] = item["Value"]
        return new_env

    def deleteRunThread(self):
        try:
            self.runThreads.pop(self.tool.workParam["MD5"])
        except:
            pass

    def clearUp(self):
        try:
            shm_a = shared_memory.SharedMemory(name=self.share_name, create=False, size=268)
            shm_a.unlink()
        except Exception as e:
            print("delShareInfo:", e)
        path = os.path.join("/data/tmp/boost_interprocess", self.share_name)
        if os.path.exists(path):
            os.remove(path)

class Tool:
    def __init__(self, workParam):
        self.workParam = workParam

def updateNotifyLostWorkConfig():
    # 将测试步骤存入离线单例类
    print("exex updateNotifyLostWorkConfig")
    # path = "lostWorkConfig.pickle"
    # lostTestStatus = LostWorkConfigMessage()
    # lostTestStatus.first_connect = False
    # fp = open(path, 'wb')
    # pickle.dump(lostTestStatus, fp)
    # fp.flush()
    # fp.close()

class ShareConnect:
    def __init__(self):
        self.share_name = None
        self.current_connect = 0
        self.port = 0
        self.current_run = 0


if __name__ == '__main__':
    workParam = dict()

    workParam["Tool"] = r"/home/lyf/桌面/pytool/ssd-script-tool/linux/testWorkcfg_test/main.py"
    workParam["Config"] = r"/home/lyf/下载/Update.txt"
    workParam["Device"] = "/dev/sda"
    workParam["Port"] = 9999
    workParam["Index"] = 1
    workParam["ToolID"] = -2147483392
    workParam["LogDir"] = "/home"
    tool = Tool(workParam)
    from queue import Queue
    queue = Queue()
    # dataPath = r"/home/lyf/桌面/pyclient/pyclient/nettestclient_python/cmpLib/data.json"
    # with open(dataPath, "r") as f:
    #     lostWorkConfig = json.loads(f.read())
    #     lostWorkConfig = json.dumps(lostWorkConfig)
    #     print(lostWorkConfig)
    port = 8001
    a = CMPClientWork(tool,queue,2,3,updateNotifyLostWorkConfig,5,port,None)
    a.getShareInfo()
    a.setClientParam()
    result = a.connectTool()
    print("result:",result)
    a.run(True)



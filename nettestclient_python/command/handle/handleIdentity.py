import json
import pickle
import subprocess

import socket
import os
import threading
import uuid
import command.handle.handleBase as handleBase

from command.event.EventPacketText import EventPacketText
import command.cmd.define as defines
import config.config as config
import command.cmd.text.packetCmd as packetCmd
from command.interfaces.netSend import NetSend
from common.ledControl import LedControl
from common.lostWorkConfigMessage import LostWorkConfigMessage
from common.systemCommon import get_host_type, is_valid_datetime, get_platform, get_etc_version_info
from command.handle.updateCompomenFile import UpdateCompomenFile


class HandleIdentify(handleBase.HandleBase):
    def __init__(self, next, netSend: NetSend) -> None:
        print("identify init")
        super().__init__(next, netSend)
        self.first_connect = True
        self.already_run = False

    def lostIdentify(self):
        path = "lostWorkConfig.pickle"
        if os.path.exists(path):
            lostWorkConfig_new = LostWorkConfigMessage()
            with open(path, 'rb') as fp:
                lostWorkConfig = pickle.load(fp)
            self.first_connect = lostWorkConfig.first_connect
            lostWorkConfig_new.set(lostWorkConfig)
            return False
        return True

    @staticmethod
    def getMac():
        # currtPlatform = platform.system().lower()
        # if currtPlatform == "windows":
        #     mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        #     mac_1 = "-".join([mac[e:e+2] for e in range(0, 11, 2)]).upper()
        #     return mac_1
        # elif currtPlatform == "linux":
        #     count = 3
        #     for i in range(count):
        #         cmd = "cat /sys/class/net/$(ip route show default | awk 'NR==1' | awk '/default/ {print $5}')/address"
        #         ret = subprocess.run(cmd, shell=True, capture_output=True)
        #         message = ret.stdout.decode().replace(":", "-").upper().replace(" ", "").replace("\n", "").replace("\r",
        #                                                                                                            "")
        #         return message
        #     print("not get mac addr")
        #     sys.exit()
        host_type = get_host_type()
        if host_type == "windows":
            mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
            mac = "-".join([mac[e:e+2] for e in range(0, 11, 2)]).upper()
        elif host_type == "MTK":
            path = "/data/mac.txt"
            if os.path.exists(path):
                with open(path, "r") as f:
                    mac = f.read()
        else:
            cmd = "cat /sys/class/net/$(ip route show default | awk 'NR==1' | awk '/default/ {print $5}')/address"
            ret = subprocess.run(cmd, shell=True, capture_output=True)
            mac = ret.stdout.decode().replace(":", "-").upper().replace(" ", "").replace("\n", "").replace("\r", "")
        return mac


    def getHostInfo(self):
        c = config.Config()
        HostType = get_host_type()
        info = {
            "HostName": socket.gethostname(),
            "Version": c.settings["Version"],
            "FirstConnect": self.first_connect,
            "HostType": HostType,
            "MacAddr": HandleIdentify.getMac()
        }
        print(info)
        # if self.virtualNode:  # 不为None表示已传入虚拟节点
        # # if "VirtualHost" in c.settings and "Enable" in c.settings["VirtualHost"] and c.settings["VirtualHost"]["Enable"]:
        # #     host = HostAddrs(virtualNode=self.virtualNode, funName="HostAddrs")
        # #     if host.host != None:
        # #         info = host.host
        # #     else:
        #     info["HostName"] = f"{self.virtualNode['HostName']}"
        #     info["VirtualMacAddr"] = f"{self.virtualNode['VirtualMacAddr']}"
        #     info["VirtualIPAddress"] = f"{self.virtualNode['VirtualIPAddress']}"
        #     # host.host = info
        return info

    def handle_default(self, event) -> bool:
        if not isinstance(event, EventPacketText):
            return False
        if event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_INDETITY.value:
            flag = self.lostIdentify()
            identify = self.getHostInfo()
            cmd = packetCmd.PacketCmd()
            cmd.cmd = defines.NCMD_TYPE.NCMD_INDETITY.value
            cmd.packet_type = defines.PACKET_TYPE.PACKET_RESPONSE.value
            self.sendCmdText(cmd, json.dumps(identify))
            if self.first_connect:
                check_app = threading.Thread(target=self.check_component)
                check_app.start()
            self.first_connect = False

            if flag:
                LedControl.online()
                return True
            # else:
            #     if not self.already_run:
            #         event.packet_cmd.cmd = defines.NCMD_TYPE.NCMD_CONTINUE_START_TEST.value
            #         self.already_run = True
        elif event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_SET_SYSTEM_TIME.value:
            server_time = event.packet_cmd.data
            current_time = f'{server_time.get("Year")}-{server_time.get("Month")}-{server_time.get("Day")} ' + \
                           f'{server_time.get("Hour")}:{server_time.get("Minute")}:{server_time.get("Second")}'
            print(f"parse server time:{current_time}")
            if is_valid_datetime(current_time):
                cmd_args = ["date", "-s", current_time]
                ret = subprocess.run(cmd_args, capture_output=True)
                print(ret)
            return True
        return False

    def check_component(self):
        '''
        检测组件
        :return:
        '''
        conf = config.Config()
        platformName = get_host_type()
        compomentList = conf.settings["component"].get(platformName)
        if compomentList:
            for compomenFile in compomentList:
                updateFile = UpdateCompomenFile(None, self.net_send)
                print(f"check new compomenFile version:{compomenFile}")
                updateFile.check_version(compomenFile)
                updateFile.wait()


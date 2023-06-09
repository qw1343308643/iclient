import copy
import json
import os
import threading
from time import sleep
import command.handle.handleBase as handleBase
from command.cmd.text.testStatusMessage import TestStatusMessage
from command.event.EventPacketText import EventPacketText
import command.cmd.define as defines
from command.cmd.text.packetCmd import PacketCmd
from command.handle.HandlePriority import HandlePriority
from command.handle.commandText import CommandText
from command.interfaces.netSend import NetSend
from common.deviceStatus import DeviceStatus
from utility.fileLock import CFileLock


class HandleTestMessage(handleBase.HandleBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)
        testStatus = TestStatusMessage()
        self.save = testStatus.save
        self.offline_info_path = "lostTestStatus.json"

    def handle_default(self, event) -> bool:
        if event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_GET_OFFLINE_INFO.value:
            self.processOfflineInfo()
            # 继续往下传递，不能返回True
            # pass
        return False

    def sendTestMessage(self, device: str, index: int, deviceStatus: DeviceStatus, ack_type) -> bool:
        testStatus = deviceStatus.toTestStatus(device, index)
        text = testStatus.toJson()
        cmd = PacketCmd()
        cmd.cmd = defines.NCMD_TYPE.NCMD_TEST_MESSAGE.value
        if ack_type == 1:
            cmd.ack_type = ack_type
            return self.sendNeedAckCmdTestMessage(cmd, text)
        return self.sendCmdText(cmd, text)

    def sendNeedAckCmdTestMessage(self, cmd, text):
        commandText = CommandText(None, self.net_send)
        HandlePriority.add_instance(commandText)
        # self.sendCmdText(cmd, text)
        commandText.send(text, cmd)
        ret = commandText.wait(10)
        HandlePriority.remove_instance(commandText)
        return ret

    def onSetStatus(self, device: str, index: int, deviceStatus: DeviceStatus, ack_type):
        if hasattr(deviceStatus, "status_id"):
            print(f"device:{device}, index:{index}, satusID:{deviceStatus.status_id},toolID:{deviceStatus.tool_id}, extrainfo:{deviceStatus.status}")
        else:
            print(
                f"device:{device}, index:{index}, toolID:{deviceStatus.tool_id}, extrainfo:{deviceStatus.status}")
        print(f"code:{deviceStatus.error_code}, times:{deviceStatus.error_times}")
        if not self.net_send.isConnect:
            self.addLostDeviceStatus(device, index, deviceStatus)
            return
        while(True):
            bRet = self.sendTestMessage(device, index, deviceStatus, ack_type)
            if bRet:
                break
            if not self.net_send.isConnect():
                self.addLostDeviceStatus(device, index, deviceStatus)
                break
            sleep(1)

    def addLostDeviceStatus(self, device: str, index: int, deviceStatus: DeviceStatus):
        print("addLostDeviceStatus")
        """
        if save:
            lostStatusDict = {'index1':[lostStatus1, lostStatus2, ...], 'index2':[lostStatus1, lostStatus2, ...], ...}
        else:
            lostStatusDict = {'index1':[lostStatusNew], 'index2':[lostStatusNew], ...}
        """ 
        testStatus = deviceStatus.toTestStatus(device, index)
        status_id = testStatus.status_id
        text = testStatus.toJson()
        path = self.offline_info_path
        fileLock = CFileLock(path)
        if fileLock.acquire():
            try:
                status_id = str(status_id)  # 转化为字符串 json.dump会将 int 转 str
                lostStatusDict = None
                if os.path.exists(path):
                    with open(path, "r") as f:
                        lostStatusDict = json.load(f)
                if self.save:
                    if isinstance(lostStatusDict, dict):
                        if lostStatusDict.get(status_id):
                            if isinstance(lostStatusDict[status_id], list):
                                lostStatusDict[status_id].append(text)
                            else:
                                status = [text]
                                lostStatusDict[status_id] = status
                        else:
                            status = [text]
                            lostStatusDict[status_id] = status
                    else:
                        lostStatusDict = {}
                        lostStatusDict[status_id] = [text]
                else:
                    lostStatusDict = {}
                    lostStatusDict[status_id] = [text]
                with open(path, "w") as f:
                    json.dump(lostStatusDict, f, indent=4)
                    f.flush()
                    os.fsync(f.fileno())
            finally:
                fileLock.release()

    # 当前的测试信息
    def processOfflineInfo(self):
        path = self.offline_info_path
        if os.path.exists(path):
            fileLock = CFileLock(path)
            if fileLock.acquire():
                try:
                    with open(path, "r") as f:
                        lostStatusDict = json.load(f)
                        if isinstance(lostStatusDict, dict):
                            for status_id, lostStatusList in lostStatusDict.items():
                                sendList = copy.copy(lostStatusList)  # 记录发送成功的列表
                                for status in lostStatusList:
                                    ret = self.onOffLineStatus(status)
                                    if ret:
                                        sendList.remove(status)
                                    else:
                                        break
                                    sleep(1)
                                lostStatusDict[status_id] = sendList
                    with open(path, "w") as f:
                        json.dump(lostStatusDict, f, indent=4)
                        f.flush()
                        os.fsync(f.fileno())
                finally:
                    fileLock.release()

    # 发送离线消息
    def onOffLineStatus(self, status):
        if not self.net_send.isConnect:
            return False
        while 1:
            cmd = PacketCmd()
            cmd.cmd = defines.NCMD_TYPE.NCMD_GET_OFFLINE_INFO.value
            cmd.sub_cmd = defines.NCMD_TYPE.NCMD_TEST_MESSAGE.value
            cmd.data = status
            return self.sendCmdText(cmd, status)
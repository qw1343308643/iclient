import copy
import json

import os
import command.handle.handleBase as handleBase
from command.cmd.binary.cmdHeader import CmdHeader
import command.cmd.define as defines
import command.cmd.binary.packetCmdLogFile as packetCmdLogFile
from command.handle.HandlePriority import HandlePriority
from command.handle.commandBinary import CommandBinary
from command.interfaces.netSend import NetSend
from command.cmd.binary.packetCmd import PacketCmd as PacketCmdB
from utility.fileLock import CFileLock
from command.event.eventPacketBinary import EventPacketBinary
from time import sleep

FILE_SIZE_PER_ONE = 64*1024


class HandleLogFile(handleBase.HandleBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)
        self.offline_log_path = "lostTestLog.json"
        self.sendFilePath = None


    def handle_default(self, event) -> bool:
         # 离线确认包
        if isinstance(event, EventPacketBinary) and event.packet_cmd.packet_type == defines.PACKET_TYPE.PACKET_ACK.value:
            print("offline packet ack:", event.packet_cmd.cmd, event.packet_cmd.packet_type, event.packet_cmd.ack_type)
            if event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_LOG_FILE.value:
                print("log set")
                self.ack_event.set()
                return True
        if event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_GET_OFFLINE_INFO.value:
            self.sendOfflineLogs()
            # 继续往下传递，不能返回True
        return False

    # 当前的测试日志
    def sendOfflineLogs(self):
        """
        logStatus:[(logFile, index, device, toolID), ...]
        sendFile(filePath: str, item: int, device: str, toolID: int)
        """
        path = self.offline_log_path
        if os.path.exists(path):
            fileLock = CFileLock(path)
            if fileLock.acquire():
                try:
                    with open(path, "r") as f:
                        lostLogDict = json.load(f)
                        if isinstance(lostLogDict, dict):
                            for index, logStautusList in lostLogDict.items():
                                sendList = copy.copy(logStautusList)
                                for logStatus in logStautusList:
                                    ret = self.sendFile(logStatus[0], int(logStatus[1]), logStatus[2], logStatus[3], offline=True)
                                    if ret:
                                        sendList.remove(logStatus)
                                    else:
                                        continue
                                lostLogDict[index] = sendList
                    with open(path, "w") as f:
                        json.dump(lostLogDict, f, indent=4)
                        f.flush()
                        os.fsync(f.fileno())
                finally:
                    fileLock.release()


    def onSetDeviceLog(self, device: str, item: int, statusID: str, logFile: str, ack_type) -> bool:
        if not self.net_send.isConnect():
            self.addLostLogFiles(item, device, statusID, logFile)
            return True
        bRet = False
        while(True):
            bRet = self.sendFile(logFile, item, device, statusID, ack_type=ack_type)
            print(f"device:{device},index:{item}, onSetDeviceLog Ret:{bRet}")
            if bRet:
                break
            if not self.net_send.isConnect():
                self.addLostLogFiles(item, device, statusID, logFile)
                break
            sleep(1)
        return True

    def sendFile(self, filePath: str, item: int, device: str, statusID: str, offline=False, ack_type=0):
        # 定义发送的header
        print("send log file")
        header = CmdHeader(None)
        cmd = PacketCmdB(header)

        if offline:
            print("发送离线信息码")
            cmd.cmd = defines.NCMD_TYPE.NCMD_GET_OFFLINE_INFO.value  # 发送离线文件命令码
            cmd.sub_cmd = defines.NCMD_TYPE.NCMD_LOG_FILE.value
        else:
            cmd.cmd = defines.NCMD_TYPE.NCMD_LOG_FILE.value  # 发送文件名命令码 44
        file_info = os.stat(filePath)
        nums = (file_info.st_size + FILE_SIZE_PER_ONE - 1)//FILE_SIZE_PER_ONE
        with open(filePath, "rb") as f:
            readed_size = 0
            read_per_one = FILE_SIZE_PER_ONE
            for i in range(nums):
                isReadFull = True
                if read_per_one + readed_size >= file_info.st_size:
                    read_per_one = file_info.st_size - readed_size
                if i + 1 == nums:
                    isReadFull = False
                log_message = packetCmdLogFile.PacketCmdLogFile(item, statusID)
                log_message.fillFileContent(
                    f, readed_size, read_per_one, isReadFull)
                readed_size += len(log_message.buf)
                if log_message.is_complete:
                    cmd.ack_type = 1
                data = log_message.getBytes()
                header.length = header.getHeaderLen() + len(data)
                value = cmd.getBytes() + data
                data = value[:8] + value[12:0]
                # data确保4字节对齐
                if len(data) % 4 != 0:
                    data += bytes(4 - len(data) % 4)
                # 计算异或值
                checkXor = 0
                for i in range(0, len(data), 4):
                    checkXor ^= int.from_bytes(data[i:i + 4], "little")
                # data pack合并
                targetData = value[:8] + int.to_bytes(checkXor, 4, "little", signed=False) + value[12:]
                if log_message.is_complete:
                    print(f"log_message.is_complete:{log_message.is_complete}")
                    flag = self.sendNeedAckCmdLog(targetData, filePath, cmd)
                else:
                    flag = self.net_send.sendData(targetData)
                if flag == False:
                    return False
        return True

    def sendNeedAckCmdLog(self, targetData, filePath, cmd):
        commandBinary = CommandBinary(None, self.net_send)
        HandlePriority.add_instance(commandBinary)
        commandBinary.send(targetData, cmd)
        # self.net_send.sendData(targetData)
        print("send ack log wait")
        ret = commandBinary.wait(600)
        if ret:
            if os.path.exists(filePath):
                os.remove(filePath)
        HandlePriority.remove_instance(commandBinary)
        return ret

    def addLostLogFiles(self, index: int, device: str, statusID: str, logFile: str):
        path = self.offline_log_path
        fileLock = CFileLock(path)
        if fileLock.acquire():
            try:
                index = str(index)
                if os.path.exists(path):
                    with open(path, "r") as f:
                        lostLogDict = json.load(f)
                    if isinstance(lostLogDict, dict):
                        if lostLogDict.get(index):
                            if isinstance(lostLogDict[index], list):
                                lostLogDict[index].append((logFile, index, device, statusID))
                            else:
                                logStatus = [(logFile, index, device, statusID)]
                                lostLogDict[index] = logStatus
                        else:
                            logStatus = [(logFile, index, device, statusID)]
                            lostLogDict[index] = logStatus
                    else:
                        lostLogDict = {}
                        lostLogDict[index] = [(logFile, index, device, statusID)]
                else:
                    lostLogDict = {}
                    lostLogDict[index] = [(logFile, index, device, statusID)]
                with open(path, "w") as f:
                    json.dump(lostLogDict, f, indent=4)
                    f.flush()
                    os.fsync(f.fileno())
            finally:
                fileLock.release()

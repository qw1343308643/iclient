import json
import os
import struct
import subprocess
from datetime import datetime

from cmpCommand.cmd.cmpdata import CMP_DEVICE_STATUS, CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE, PACKET_TYPE
from cmpCommand.ledControl import LedControl

class CmpClientHandleTestStatus(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp
        self.isEnd = False

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_STATUS.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_STATUS.value
            cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
            nItem = self.cmp.tool.workParam["Index"]
            data = int.to_bytes(nItem, 4, "little", signed=False)
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            # if len(value) % 4 != 0:  # 确保4字节对齐
            #     value += bytes(4 - len(value) % 4)
            print("send get status command")
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_STATUS.value and event.packet_cmd.packet_type == PACKET_TYPE.PACKET_RESPONSE.value:
            print("get status")
            cmd = event.packet_cmd
            deviceStatus = CMP_DEVICE_STATUS.parse(cmd.data)
            ack_type = 0
            if (deviceStatus.bRun == False or deviceStatus.bFinished == True) and self.isEnd == False:
                if deviceStatus.dwErrorTimes != 0 or deviceStatus.bFinished == False or deviceStatus.dwErrorCode != 0:
                    self.cmp.tool.error_flag = True
                    LedControl.testError()
                    getSystemLog()
                # 发送获取日志命令
                self.cmp.tool.endTime = datetime.now()
                self.cmp.cmd_pipe.put(
                    (CMP_CMD_TYPE.CMP_SEND_LOG.value, 0, PACKET_TYPE.PACKET_NOMAL.value, ACK_TYPE.NEED_RESPONSE.value))
                ack_type = 1
                self.isEnd = True
            status = self.cmp.DeviceStatus.parse(deviceStatus)
            status_id = self.cmp.tool.workParam.get("StatusID")
            if not status_id:
                status.tool_id = self.cmp.tool.workParam.get("ToolID")
                if hasattr(status, "status_id"):
                    delattr(status, "status_id")
            else:
                status.status_id = status_id
            print(f"send tool status")
            self.cmp.onSetStatus(self.cmp.tool.workParam["Device"], self.cmp.tool.workParam["Index"], status, ack_type)
            return True

        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_WORK_CONFIG.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            workConfigMessage = self.cmp.workConfigMessage.jsonDict()
            print("workConfigMessage again:",workConfigMessage)
            stepList = []
            for step in workConfigMessage["StepConfigs"]:
                toolList = []
                stepMessage = step.jsonDict()
                for tool in stepMessage["Tools"]:
                    toolMessage = tool.jsonDict()
                    toolList.append(toolMessage)
                stepMessage["Tools"] = toolList
                stepList.append(stepMessage)
            workConfigMessage["StepConfigs"] = stepList
            workConfigMessage["Disk"] = workConfigMessage["Disk"].jsonDict()
            print("workConfigMessage later:",workConfigMessage)
            info = json.dumps(workConfigMessage)
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_WORK_CONFIG.value
            cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
            data = struct.pack(f"{len(info.encode('utf8'))}s", info.encode('utf8')) \
                   + struct.pack(f"1s", "".encode("utf8"))
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            print("send CMP_GET_WORK_CONFIG")
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_TOOL_ID.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            toolID = self.cmp.tool.workParam["ToolID"]
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_TOOL_ID.value
            cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
            data = struct.pack(f"i", toolID)
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            print("send CMP_GET_TOOL_ID")
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_STATUS_ID.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            statusID = self.cmp.tool.workParam["StatusID"]
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_STATUS_ID.value
            cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
            data = struct.pack(f"128s", statusID)
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            print("send CMP_GET_STATUS_ID")
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_REBOOT_NOTIFY.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            print("notifyreboot command")
            data = struct.unpack(f"?", event.packet_cmd.data)
            print("data:",data)
            if data[0]:
                path = "lostWorkConfig.pickle"
                if os.path.exists(path):
                    os.remove(path)
            else:
                print("updateNotifyLostWorkConfig")
                self.cmp.updateNotifyLostWorkConfig()
                print("del share memory")
                share_name = self.cmp.getShareName()
                self.cmp.tool.isReboot = True
                path = os.path.join("/data/tmp/boost_interprocess", share_name)
                if os.path.exists(path):
                    os.remove(path)
            self.notifyRebootResponse()
            return True

    def notifyRebootResponse(self):
        cmpHeader = CMPHeader(None)
        cmpHeader.cmd = CMP_CMD_TYPE.CMP_REBOOT_NOTIFY.value
        cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
        cmpHeader.length = cmpHeader.getHeaderLen()
        value = cmpHeader.getBytes()
        self.cmp.sendMessage(value)

def getSystemLog():
    if os.path.exists("/data/kernellog.txt"):
        cmd = "trigger_exception_handle /data/kernellog.txt"
        subprocess.run(cmd, shell=True, capture_output=True)


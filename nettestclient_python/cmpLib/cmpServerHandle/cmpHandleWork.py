import struct
import threading
import time

from cmpCommand.cmd.cmpdata import CMPHeader, CMP_DEVICE_STATUS
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpServerHandle.cmpHandleTestStatus import CmpHandleTestStatus
from cmpCommand.define import CMP_CMD_TYPE, PACKET_TYPE


class CmpHandleWork(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_START_TEST.value:
            data = struct.unpack("i", event.packet_cmd.data)
            nItem = data[0]
            if self.cmp.CMPClient.CMPStartTest(nItem):
                self.responseStart(True)
                app = threading.Thread(target=self.refreshTestStatusTool, args=(nItem, ))
                app.start()
                return True
            else:
                self.responseStart(False)
                return True

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_STOP_TEST.value:
            data = struct.unpack("i", event.packet_cmd.data)
            nItem = data[0]
            self.cmp.CMPClient.CMPStopTest(nItem)


        return False

    def responseStart(self, result: bool):
        cmpHeader = CMPHeader(None)
        cmpHeader.cmd = CMP_CMD_TYPE.CMP_START_TEST.value
        cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
        data = struct.pack(f"?", result)
        cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
        value = cmpHeader.getBytes() + data
        self.cmp.sendMessage(value)


    # 工具端刷新测试内容定时器
    def refreshTestStatusTool(self, nItem: int):
        while self.cmp.runFlag:
            deviceStatus = self.cmp.CMPClient.CMPGetStatus(nItem)
            self.cmp.deviceStatus = CMP_DEVICE_STATUS(deviceStatus)
            if self.cmp.deviceStatus.bFinished == True and self.cmp.deviceStatus.bRun == False:
                data = self.cmp.deviceStatus.toBytes(nItem)
                cmpHeader = CMPHeader(None)
                cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_STATUS.value
                cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
                cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
                value = cmpHeader.getBytes() + data
                self.cmp.sendMessage(value)
                return
            time.sleep(1)
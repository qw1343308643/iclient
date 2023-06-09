import struct
import subprocess
import time

from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE, PACKET_TYPE


class CmpClientHandleWorkType(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary
                          ):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_WORK_TYPE.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_WORK_TYPE.value
            cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
            cmpHeader.length = cmpHeader.getHeaderLen()
            value = cmpHeader.getBytes()
            if len(value) % 4 != 0:  # 确保4字节对齐
                value += bytes(4 - len(value) % 4)
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_WORK_TYPE.value and event.packet_cmd.packet_type == PACKET_TYPE.PACKET_RESPONSE.value:
            value = event.packet_cmd.data.decode("utf8").replace("\0", "")
            print("value:",value)
            # device_status = self.cmp.DeviceStatus()
            # device_status.finished = False
            # device_status.run = True
            # device_status.status = "Testing"
            # if value:
            #     device_status.addStatus({'Status':value})
            # self.cmp.onSetStatus(self.cmp.tool.workParam["Device"], self.cmp.tool.workParam["Index"], device_status)
            if self.cmp.fisrtConnect:
                self.cmp.cmd_pipe.put(
                    (CMP_CMD_TYPE.CMP_TEST_PARAM.value, 0, 0, ACK_TYPE.NEED_RESPONSE.value))
            else:
                self.cmp.cmd_pipe.put(
                    (CMP_CMD_TYPE.CMP_START_TEST.value, 0, 0, ACK_TYPE.NEED_RESPONSE.value))
            return True



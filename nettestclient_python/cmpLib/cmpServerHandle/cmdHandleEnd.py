import os

from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE, PACKET_TYPE
from cmpCommand.cmd.cmpdata import CMP_DEVICE_STATUS, CMPHeader


class CmpHandleEnd(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary
                          ):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_PID.value:
            print("handleEnd")
            pid = os.getpid()
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_PID.value
            cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
            data = int.to_bytes(pid, 4, "little", signed=False)
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_EXIT.value:
            self.cmp.runFlag = False
            self.cmp.client_socket.close()
            return True
        return False



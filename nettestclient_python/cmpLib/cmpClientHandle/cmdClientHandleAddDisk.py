import struct

from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE, PACKET_TYPE


class CmpClientHandleAddDisk(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary
                          ):
            return False
        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_ADD_DISK.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            print("add disk")
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_ADD_DISK.value
            cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
            data = struct.pack(f"i20s", self.cmp.tool.workParam["Index"],self.cmp.tool.workParam["Device"].encode("utf8"))
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            if len(value) % 4 != 0:  # 确保4字节对齐
                value += bytes(4 - len(value) % 4)
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_ADD_DISK.value and event.packet_cmd.packet_type == PACKET_TYPE.PACKET_RESPONSE.value:
            value = struct.unpack(f"?", event.packet_cmd.data)[0]
            if value:
                self.cmp.cmd_pipe.put(
                    (CMP_CMD_TYPE.CMP_GET_WORK_TYPE.value, 0, 0, ACK_TYPE.NEED_RESPONSE.value))
            else:
                pass
            return True



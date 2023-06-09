import struct

from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE, PACKET_TYPE


class CmpClientHandleInitInfo(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary
                          ):
            return False
        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_INIT.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            print("SEND INIT INFO CMD")
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_INIT.value
            cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
            nItem = self.cmp.tool.workParam["Index"]
            data = int.to_bytes(nItem, 4, "little", signed=False)
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_INIT.value and event.packet_cmd.packet_type == PACKET_TYPE.PACKET_RESPONSE.value:
            print("GET INIT STATUS")
            value = struct.unpack(f"?", event.packet_cmd.data)[0]
            print("init response value:",value)
            if value:
                self.cmp.cmd_pipe.put(
                    (CMP_CMD_TYPE.CMP_GET_PID.value, 0, PACKET_TYPE.PACKET_NOMAL.value, ACK_TYPE.NEED_RESPONSE.value))
            else:
                pass
            return True

    def send_cmp_init_cmd(self):
        print("SEND INIT INFO CMD")
        cmpHeader = CMPHeader(None)
        cmpHeader.cmd = CMP_CMD_TYPE.CMP_INIT.value
        cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
        nItem = self.cmp.tool.workParam["Index"]
        data = int.to_bytes(nItem, 4, "little", signed=False)
        cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
        value = cmpHeader.getBytes() + data
        self.cmp.sendMessage(value)
        ret = self.wait()
        return True

import struct

from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, PACKET_TYPE


class CmpHandleInitInfo(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_INIT.value:
            print("handleInit")
            data = struct.unpack("i", event.packet_cmd.data)
            item = data[0]
            if self.refreshDisk(item):
                self.responseAddDisk(True)
            else:
                self.responseAddDisk(False)
            return True
        return False

    def refreshDisk(self, item):
        return True
        # return self.cmp.CMPClient.CMPAddDisk(item)

    def responseAddDisk(self, result: bool):
        cmpHeader = CMPHeader(None)
        cmpHeader.cmd = CMP_CMD_TYPE.CMP_INIT.value
        cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
        data = struct.pack(f"?", result)
        cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
        value = cmpHeader.getBytes() + data
        self.cmp.sendMessage(value)

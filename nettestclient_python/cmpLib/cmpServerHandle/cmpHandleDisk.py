import struct

from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, PACKET_TYPE


class CmpHandleDisk(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_ADD_DISK.value:
            print("handleDisk")
            data = struct.unpack("i20s", event.packet_cmd.data)
            device = data[1].decode("utf8").replace("\0", "")
            item = data[0]
            if self.refreshDisk(device, item):
                self.responseAddDisk(True)
            else:
                self.responseAddDisk(False)
            return True
        return False

    def refreshDisk(self, device, item):
        # return True
        return self.cmp.CMPClient.CMPAddDisk(device, item)

    def responseAddDisk(self, result: bool):
        cmpHeader = CMPHeader(None)
        cmpHeader.cmd = CMP_CMD_TYPE.CMP_ADD_DISK.value
        cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
        data = struct.pack(f"?", result)
        cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
        value = cmpHeader.getBytes() + data
        self.cmp.sendMessage(value)

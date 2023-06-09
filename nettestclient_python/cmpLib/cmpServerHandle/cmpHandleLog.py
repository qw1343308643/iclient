import struct

from cmpCommand import cmpHandleBase
from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand.define import CMP_CMD_TYPE, PACKET_TYPE


class CmpHandleLog(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary
                          ):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_LOG.value:
            print("handleLog")
            data = struct.unpack("i", event.packet_cmd.data)
            nItem = data[0]
            value = self.getValue(nItem)
            self.cmp.sendMessage(value)
            return True
        return False


    def getValue(self, nItem):
        nStrLog = self.cmp.CMPClient.CMPGetLogs(nItem)
        if nStrLog == None:
            nStrLog = ""
        cmpHeader = CMPHeader(None)
        cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_LOG.value
        cmpHeader.packet_type = PACKET_TYPE.PACKET_NOMAL.value
        nSize = struct.calcsize(f"2i{len(nStrLog.encode('utf8'))}s")
        data = int.to_bytes(nSize, 4, "little", signed=False) + \
               int.to_bytes(nItem, 4, "little", signed=False) + \
               struct.pack(f"{len(nStrLog.encode('utf8'))}s", nStrLog.encode("utf8"))
        cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
        value = cmpHeader.getBytes() + data
        return value

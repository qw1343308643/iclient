import struct

from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, PACKET_TYPE


class CmpHandleTestName(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_WORK_TYPE.value:
            print("handleTestName")
            tool_name = self.cmp.CMPClient.CMPGetCustomInfo(0)  # 获取工作名称
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_WORK_TYPE.value
            cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
            data = struct.pack(f"{len(tool_name.encode('utf8'))}s", tool_name.encode("utf8"))
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            self.cmp.sendMessage(value)
            return True
        return False


import struct

from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, PACKET_TYPE


class CmpHandleTestSetting(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_TEST_PARAM.value:
            print("handleTestSetting")
            config_len = len(event.packet_cmd.data) - struct.calcsize(f"i260s")
            print("config_len:",config_len)
            print(event.packet_cmd.data)
            data = struct.unpack(f"i260s{config_len}s", event.packet_cmd.data)
            nSize = data[0]
            _strLogDir = data[1].decode("utf8").replace("\0", "")
            _strConfig = data[2].decode("utf8").replace("\0", "")
            print(f"_strLogDir:{_strLogDir}")
            print(f"_strConfig:{_strConfig}")
            if self.cmp.CMPClient.CMPPreStart(_strLogDir, _strConfig):
                self.responseParam(True)
                return True
            else:
                self.cmp.runFlag = False
                self.responseParam(False)
                return True
        return False

    def responseParam(self, result: bool):
        cmpHeader = CMPHeader(None)
        cmpHeader.cmd = CMP_CMD_TYPE.CMP_TEST_PARAM.value
        cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
        data = struct.pack(f"?", result)
        cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
        value = cmpHeader.getBytes() + data
        self.cmp.sendMessage(value)
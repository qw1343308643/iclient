import json
import struct
import sys

from cmpCommand.cmd.cmpdata import CMP_DEVICE_STATUS, CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE, PACKET_TYPE


class CmpHandleTestStatus(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_STATUS.value:
            print("tool server get status")
            data = struct.unpack("i", event.packet_cmd.data)
            nItem = data[0]
            deviceStatus = self.cmp.CMPClient.CMPGetStatus(nItem)
            self.cmp.deviceStatus = CMP_DEVICE_STATUS(deviceStatus)
            data = self.cmp.deviceStatus.toBytes(nItem)
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_STATUS.value
            cmpHeader.packet_type = PACKET_TYPE.PACKET_RESPONSE.value
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_WORK_CONFIG.value:
            data = struct.unpack(f"{len(event.packet_cmd.data)}s", event.packet_cmd.data)[0]
            data = data.decode('utf8').replace("\0", "")
            info = json.loads(data)
            self.cmp.workCfg = info
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_TOOL_ID.value
            cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
            cmpHeader.length = cmpHeader.getHeaderLen()
            value = cmpHeader.getBytes()
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_TOOL_ID.value:
            toolID = struct.unpack(f"i", event.packet_cmd.data)[0]
            print("toolID:", toolID)
            self.cmp.workCfg = toolID
            return True

        return False



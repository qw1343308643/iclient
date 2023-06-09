import struct
import threading
import time
from datetime import datetime

from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand import cmpHandleBase
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE, PACKET_TYPE


class CmpClientHandleWork(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary):
            return False

        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_STOP_TEST.value:
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_STOP_TEST.value
            cmpHeader.ack_type = ACK_TYPE.NEED_NONE.value
            nItem = self.cmp.tool.workParam["Index"]
            data = int.to_bytes(nItem, 4, "little", signed=False)
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            if len(value) % 4 != 0:  # 确保4字节对齐
                value += bytes(4 - len(value) % 4)
            self.cmp.sendMessage(value)
            return True

        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_TEST_PARAM.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_TEST_PARAM.value
            cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
            _strLogDir = self.cmp.tool.workParam["LogDir"]
            _strConfig = self.cmp.tool.workParam["Config"]
            nSize = struct.calcsize(f"i260s{len(_strConfig.encode('utf8'))}s")
            data = int.to_bytes(nSize, 4, "little", signed=False) \
                   + struct.pack(f"260s", _strLogDir.encode("utf8")) \
                   + struct.pack(f"{len(_strConfig.encode('utf8'))}s", _strConfig.encode("utf8"))\
                   + struct.pack(f"1s", "".encode("utf8"))
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_TEST_PARAM.value and event.packet_cmd.packet_type == PACKET_TYPE.PACKET_RESPONSE.value:
            value = struct.unpack(f"?", event.packet_cmd.data)[0]
            print("test param value:",value)
            if value:
                self.cmp.cmd_pipe.put(
                    (CMP_CMD_TYPE.CMP_START_TEST.value, 0, 0, ACK_TYPE.NEED_RESPONSE.value))
            else:
                self.cmp.cmd_pipe.put(
                    (CMP_CMD_TYPE.CMP_EXIT.value, 0, PACKET_TYPE.PACKET_NOMAL.value, ACK_TYPE.NEED_NONE.value))
            return True

        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_START_TEST.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            print("start Test")
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_START_TEST.value
            cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
            nItem = self.cmp.tool.workParam["Index"]
            data = int.to_bytes(nItem, 4, "little", signed=False)
            # if len(data) % 4 != 0:
            #     data += bytes(4 - len(data) % 4)
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_START_TEST.value and event.packet_cmd.packet_type == PACKET_TYPE.PACKET_RESPONSE.value:
            print("start Test True")
            value = struct.unpack(f"?", event.packet_cmd.data)[0]
            self.cmp.tool.startTime = datetime.now()
            time.sleep(3)
            self.cmp.cmd_pipe.put(
                (CMP_CMD_TYPE.CMP_GET_STATUS.value, 0, 0, ACK_TYPE.NEED_RESPONSE.value))
            refreshTestStatusTimer = threading.Thread(target=self.cmp.refreshTestStatusTimer)  # 定时刷新
            refreshTestStatusTimer.start()
            if not value:
                self.cmp.cmd_pipe.put(
                    (CMP_CMD_TYPE.CMP_EXIT.value, 0, PACKET_TYPE.PACKET_NOMAL.value, ACK_TYPE.NEED_NONE.value))
            return True



import os
import platform
import struct
import subprocess
import time
from cmpCommand import cmpHandleBase
from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE, PACKET_TYPE



class CmpClientHandleEnd(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp
        self.fisrtGet = True

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary
                          ):
            return False
        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_PID.value and event.packet_cmd.ack_type == ACK_TYPE.NEED_RESPONSE.value:
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_PID.value
            cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
            nItem = self.cmp.tool.workParam["Index"]
            data = int.to_bytes(nItem, 4, "little", signed=False)
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            self.cmp.sendMessage(value)
            return True
        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_PID.value and event.packet_cmd.packet_type == PACKET_TYPE.PACKET_RESPONSE.value:
            print("get pid:",event.packet_cmd.data)
            pid = struct.unpack("i", event.packet_cmd.data)[0]
            print(pid)
            self.cmp.pid.append(pid)
            self.cmp.cmd_pipe.put(
                (CMP_CMD_TYPE.CMP_ADD_DISK.value, 0, 0, ACK_TYPE.NEED_RESPONSE.value))
            # self.close_tool(pid)
            # print("close tool process")
            # self.cmp.runFlag = False
            # self.cmp.tool.run = False
            # self.cmp.tcp_client.close()
            return True

        elif event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_EXIT.value:

            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_EXIT.value
            cmpHeader.ack_type = ACK_TYPE.NEED_NONE.value
            nItem = self.cmp.tool.workParam["Index"]
            data = int.to_bytes(nItem, 4, "little", signed=False)
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            self.cmp.sendMessage(value)
            self.cmp.runFlag = False
            self.cmp.tool.run = False
            self.cmp.tool.isReboot = False
            self.close_tool()

            print(f"device:{self.cmp.tool.workParam['Device']},index:{self.cmp.tool.workParam['Index']},close tool process!")
            self.cmp.tcp_client.close()
            return True

    def close_tool(self):
        if platform.system().lower() == "windows":
            pass
        elif platform.system().lower() == "linux":
            print("close linux tool ip list:", self.cmp.pid)
            pids = list(reversed(self.cmp.pid))
            for pid in pids:
                self.close_linux_tool(pid)

    def close_linux_tool(self, pid):
        try:
            os.kill(pid, 0)
            term_cmd = f"kill -s 15 {pid}"
            print("term cmd:", term_cmd)
            subprocess.run(term_cmd, shell=True, capture_output=True)
            print("send sign term")
        except:
            return
        time.sleep(1)
        try:
            os.kill(pid, 0)
            kill_cmd = f"kill -s 9 {pid}"
            print("kill cmd:", kill_cmd)
            subprocess.run(kill_cmd, shell=True, capture_output=True)
        except:
            return
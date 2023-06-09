import os
import struct
import subprocess

from cmpCommand import cmpHandleBase
from cmpCommand.cmd.cmpdata import CMPHeader
from cmpCommand.event.cmpEventPacketBinary import CmpEventPacketBinary
from cmpCommand.define import CMP_CMD_TYPE, ACK_TYPE, PACKET_TYPE


class CmpClientHandleLog(cmpHandleBase.CmpHandleBase):
    def __init__(self, next, cmp) -> None:
        super().__init__(next, cmp)
        self.cmp = cmp
        self.finishCount = 0

    def handle_default(self, event) -> bool:
        if not isinstance(event, CmpEventPacketBinary
                          ):
            return False

        # 发送获取日志命令
        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_SEND_LOG.value:
            cmpHeader = CMPHeader(None)
            cmpHeader.cmd = CMP_CMD_TYPE.CMP_GET_LOG.value
            cmpHeader.ack_type = ACK_TYPE.NEED_RESPONSE.value
            nItem = self.cmp.tool.workParam["Index"]
            data = int.to_bytes(nItem, 4, "little", signed=False)
            cmpHeader.length = cmpHeader.getHeaderLen() + len(data)
            value = cmpHeader.getBytes() + data
            # if len(value) % 4 != 0:  # 确保4字节对齐
            #     value += bytes(4 - len(value) % 4)
            self.cmp.sendMessage(value)
            return True

        # 接收日志
        if event.packet_cmd.cmd == CMP_CMD_TYPE.CMP_GET_LOG.value:
            # 接收数据
            share_cnt = self.cmp.runThreads.get(self.cmp.tool.workParam["MD5"])
            if share_cnt:
                run_count = share_cnt.current_run - 1
                share_cnt.current_run = run_count
            else:
                run_count = 0
            self.cmp.runThreads[self.cmp.tool.workParam["MD5"]] = share_cnt
            data = struct.unpack(f"2i{len(event.packet_cmd.data[8:])}s", event.packet_cmd.data)
            nStrLogList = data[2].decode("utf8").split("\n")
            if os.path.exists("/sys/led_control/red_led"):
                cmd = "cat /sys/led_control/red_led"
                ret = subprocess.run(cmd, shell=True, capture_output=True)
                if ret.stdout.decode() == "66050":
                    if os.path.exists("/data/kernellog.txt"):
                        nStrLogList.append("/data/kernellog.txt")
            for nStrLog in nStrLogList:
                if not os.path.isdir(nStrLog) and os.path.exists(nStrLog):
                    test_id = self.cmp.tool.workParam.get("StatusID")
                    if not test_id:
                        test_id = self.cmp.tool.workParam.get("ToolID")
                    print("send onSetDeviceLog ")
                    self.cmp.onSetDeviceLog(self.cmp.tool.workParam["Device"], self.cmp.tool.workParam["Index"],
                                            test_id, nStrLog, ack_type=1)  # 上传测试日志
                    print("onSetDeviceLog finish")
            print(f"device:{self.cmp.tool.workParam['Device']},index:{self.cmp.tool.workParam['Index']}, run_count:{run_count}")
            if run_count <= 0:
                # 通知工具退出
                self.cmp.cmd_pipe.put(
                    (CMP_CMD_TYPE.CMP_EXIT.value, 0, PACKET_TYPE.PACKET_NOMAL.value, ACK_TYPE.NEED_NONE.value))
            return True


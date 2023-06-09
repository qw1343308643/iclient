from __future__ import annotations

import hashlib
import os
import threading

import command.interfaces.netSend as netSend
import command.interfaces.netPacketSend as netPacketSend
import command.cmd.text.packetCmd as packetCmd
import command.cmd.binary.packetCmd as bpacketCmd
from command.cmd.binary.cmdHeader import CmdHeader


class CommandBase(netPacketSend.NetPacketSend):
    def __init__(self, next: CommandBase, netSend: netSend.NetSend) -> None:
        self.next = next
        self.net_send = netSend
        self.event = threading.Event()
        self.cmd = 0
        self.sub_cmd = 0
        self.packet_type = 0
        self.ack_type = 0

    def handle(self, event):
        processed = False
        handler = f"handle_{event}"
        if hasattr(self, handler):
            methond = getattr(self, handler)
            processed = methond(event)

        if hasattr(self, "handle_default"):
            processed = self.handle_default(event)

        if self.next and not processed:
            processed = self.next.handle(event)
        return processed

    def offline(self):
        if not self.event.isSet():
            self.event.set()

    def online(self):
        pass

    def send(self, data, cmd):
        if cmd.ack_type == 1:
            self.cmd = cmd.cmd
            self.packet_type = cmd.ack_type
        print(f"send data type:{type(data)}")
        print(f"cmd:{cmd.cmd}, cmd:acK:{cmd.ack_type}")
        if type(data) == str:
            print("send str")
            return self.sendCmdText(cmd, data)
        elif type(data) == bytes:
            print("send byte")
            return self.net_send.sendData(data)


    def sendCmdText(self, cmd: packetCmd.PacketCmd, text: str) -> bool:
        cmd.data = text
        response = cmd.toJson()
        return self.net_send.sendMessage(response)

    def sendCmdBytes(self, cmdType: int, subCmd: int, packetType: int, ackType: int, buf: bytes) -> bool:
        header = CmdHeader(None)
        cmd = bpacketCmd.PacketCmd(header)
        cmd.cmd = cmdType
        cmd.sub_cmd = subCmd
        cmd.packet_type = packetType
        cmd.ack_type = ackType
        cmd.data = buf
        return self.net_send.sendData(cmd.getBytes())

    def wait(self, timeOut=None):
        ret = self.event.wait(timeOut)
        print("wait ret:", ret)
        return ret

    def getFileMD5(self, filePath: str) -> str :
        filePath = filePath.replace("\\", os.sep)
        with open(filePath, 'rb') as f:
            md5 = hashlib.md5()
            md5.update(f.read())
            md5 = md5.hexdigest()
            f.close()
        return md5 .upper()

    def writeFile(self, file_data, file_path):
        log_dir = os.path.dirname(file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if not file_data.offset:
            if os.path.exists(file_path):
                os.remove(file_path)
        with open(file_path, "ab+") as f:
            f.seek(file_data.offset)
            f.write(file_data.buf)
            f.flush()
            os.fsync(f.fileno())
        if file_data.is_complete:
            return True
        return False
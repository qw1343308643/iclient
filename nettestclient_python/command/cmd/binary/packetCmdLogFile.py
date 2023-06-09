import struct
import os
import command.cmd.binary.cmdFileMessage as cmdFileMessage


class PacketCmdLogFile(cmdFileMessage.CmdFileMessage):
    def __init__(self, index=None, statusID=None) -> None:
        super().__init__()
        self.index = index
        self.status_id = statusID
        self.recv = bytearray()

    def getBytes(self):
        return struct.pack("i128s132s", self.index, str(self.status_id).encode('utf-8'), self.recv) + super().getBytes()

    def fillFileMessage(self, fileMessage: cmdFileMessage.CmdFileMessage):
        self.file_name = fileMessage.file_name
        self.offset = fileMessage.offset
        self.len = fileMessage.len
        self.is_complete = fileMessage.is_complete
        self.buf = fileMessage.buf

    def fillFileContent(self, f, offset: int, nums: int, isReadFull: bool):
        file_message = cmdFileMessage.CmdFileMessage.createFromFile(
            f, offset, nums, isReadFull)
        self.fillFileMessage(file_message)

    @staticmethod
    def parse(data):
        head_len = struct.calcsize("2i")
        head_bytes = data[:head_len]
        log_file_message = PacketCmdLogFile()
        log_file_message.index, log_file_message.tool_id = struct.unpack(
            "2i", head_bytes)
        log_file_message.file_message = cmdFileMessage.CmdFileMessage.parse(
            data[head_len:])

        return log_file_message


if __name__ == "__main__":
    print(os.getcwd())
    index = 1
    tool_id = 8000
    log_message = PacketCmdLogFile(index, tool_id)
    log_message.file_name = "123"
    print(log_message.getBytes())

    with open(f"{os.getcwd() + os.sep}test.txt", "rb") as f:
        while(True):
            offset = 0
            mbytes, complete = log_message.getFileBytes(f, offset, 1024)
            if complete:
                break
            offset += 1024
    mbytes = log_message.getBytes()
    fie_message2 = log_message.parse(mbytes)
    print(fie_message2)

# from __future__ import annotations

import struct
import os
import time


class CmdFileMessage:
    def __init__(self, ins=None) -> None:
        if ins:
            self.file_name = ins.file_name
            self.offset = ins.offset
            self.len = ins.len
            self.is_complete = ins.is_complete
            self.buf = ins.buf
        else:
            self.file_name = ""
            self.offset = 0
            self.len = 0
            self.is_complete = 0
            self.buf = bytearray()

    def _getBytes(self):
        array_len = len(self.buf)
        return struct.pack(f"260sq2i{array_len}s", self.file_name.encode('utf8'), self.offset, self.len, self.is_complete, self.buf)

    def getBytes(self):
        return self._getBytes()

    def getFileBytes(self, f, offset, nums):
        self.file_name = os.path.basename(f.name)
        f.seek(offset, 0)
        content = f.read(nums)
        self.offset = offset
        self.len = len(content)
        self.is_complete = True if self.len < nums else False
        self.buf = content
        mbytes = self._getBytes()
        return mbytes, self.is_complete

    @staticmethod
    def createFromFile(f, offset, nums, isReadFull):
        file_message = CmdFileMessage()
        file_message.file_name = os.path.basename(f.name)
        f.seek(offset, 0)
        content = f.read(nums)
        file_message.offset = offset
        file_message.len = len(content)
        if isReadFull:
            file_message.is_complete = True if file_message.len < nums else False
        else:
            file_message.is_complete = True if file_message.len <= nums else False
        file_message.buf = content
        return file_message

    @staticmethod
    def parse(data):
        head_len = struct.calcsize("260sq2i")
        head_bytes = data[:head_len]
        packet_tuple = struct.unpack("260sq2i", head_bytes)

        file_message = CmdFileMessage()
        file_message.file_name = packet_tuple[0].decode("UTF-8")
        file_message.offset = packet_tuple[1]
        file_message.len = packet_tuple[2]
        file_message.is_complete = packet_tuple[3]
        file_message.buf = data[head_len:]
        return file_message


if __name__ == "__main__":
    print(os.getcwd())
    fileMessage = CmdFileMessage()
    with open(f"{os.getcwd() + os.sep}test.txt", "rb") as f:
        while(True):
            offset = 0
            mbytes, complete = fileMessage.getFileBytes(f, offset, 1024)
            if complete:
                break
            offset += 1024
    mbytes = fileMessage.getBytes()
    fie_message2 = CmdFileMessage.parse(mbytes)
    print(fie_message2)

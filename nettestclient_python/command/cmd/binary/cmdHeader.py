import struct
import command.cmd.define as define

_PACK_FORMAT_STR = "3i4bi"


class CmdHeader:
    def __init__(self, header) -> None:
        if header is None:
            self.flag = define.NCMD_FLAG
            self.length = 0
            self.xor = 0
            self.cmd = 0
            self.sub_cmd = 0
            self.packet_type = 0
            self.ack_type = 0
            self.resv = 0
        else:
            self.flag = header.flag
            self.length = header.length
            self.xor = header.xor
            self.cmd = header.cmd
            self.sub_cmd = header.sub_cmd
            self.packet_type = header.packet_type
            self.ack_type = header.ack_type
            self.resv = header.resv

    def getBytes(self):
        return struct.pack(_PACK_FORMAT_STR, self.flag, self.length, self.xor, self.cmd,
                           self.sub_cmd, self.packet_type, self.ack_type, self.resv)

    @staticmethod
    def getHeaderLen():
        return struct.calcsize(_PACK_FORMAT_STR)

    @staticmethod
    def parse(data):
        packet_tuple = struct.unpack(_PACK_FORMAT_STR, data)
        header = CmdHeader(None)
        header.flag = packet_tuple[0]
        header.length = packet_tuple[1]
        header.xor = packet_tuple[2]
        header.cmd = packet_tuple[3]
        header.sub_cmd = packet_tuple[4]
        header.packet_type = packet_tuple[5]
        header.ack_type = packet_tuple[6]
        header.resv = packet_tuple[7]
        return header




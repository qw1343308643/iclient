import command.cmd.binary.cmdHeader as cmdHeader


class PacketCmd(cmdHeader.CmdHeader):
    def __init__(self, header) -> None:
        self.data = bytearray()
        if header is not None:
            super().__init__(header)

    @staticmethod
    def parse(data):
        if len(data) != 20:
            header = data[:20]
        else:
            header = data
        header = cmdHeader.CmdHeader.parse(header)
        cmd = PacketCmd(header)
        cmd.data = data[cmdHeader.CmdHeader.getHeaderLen():]
        return cmd

    @staticmethod
    def getTargetData(data, cmd=0, sub=0, packet_type=0, ack_type=0):
        header = cmdHeader.CmdHeader(None)
        header.length = header.getHeaderLen() + len(data)
        packetCmd = PacketCmd(header)
        packetCmd.cmd = cmd
        packetCmd.sub_cmd = sub
        packetCmd.packet_type = packet_type
        packetCmd.ack_type = ack_type
        value = packetCmd.getBytes() + data
        data = value[:8] + value[12:0]
        # data确保4字节对齐
        if len(data) % 4 != 0:
            data += bytes(4 - len(data) % 4)
        # 计算异或值
        checkXor = 0
        for i in range(0, len(data), 4):
            checkXor ^= int.from_bytes(data[i:i + 4], "little")
        # data pack合并
        targetData = value[:8] + int.to_bytes(checkXor, 4, "little", signed=False) + value[12:]
        return targetData

if __name__ == '__main__':
    value = b'+b \x16\x14\x00\x00\x00+b \x16,\x00\x01\x01\x00\x00\x00\x00'
    cmd = PacketCmd.parse(value)
    print(cmd.cmd)
    print(cmd.sub_cmd)
    print(cmd.packet_type)
    print(cmd.ack_type)
    print(cmd.data)
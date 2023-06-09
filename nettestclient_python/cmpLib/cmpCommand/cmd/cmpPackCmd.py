from cmpCommand.cmd.cmpdata import CMPHeader


class CmpPacketCmd(CMPHeader):
    def __init__(self, header) -> None:
        self.data = bytearray()
        if header is not None:
            super().__init__(header)

    @staticmethod
    def parse(data):
        if len(data) != 16:
            header = data[:16]
        else:
            header = data
        header = CMPHeader.parse(header)
        cmd = CMPHeader(header)
        cmd.data = data[CMPHeader.getHeaderLen():cmd.length]
        return cmd

    @staticmethod
    def parseCmd(data):
        cmd = CMPHeader(None)
        cmd.cmd = data[0]
        cmd.sub_cmd = data[1]
        cmd.packet_type = data[2]
        cmd.ack_type = data[3]
        return cmd

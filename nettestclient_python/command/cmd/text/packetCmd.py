import json


class PacketCmd:
    def __init__(self) -> None:
        super().__init__()
        self.cmd = 0
        self.sub_cmd = 0
        self.packet_type = 0
        self.ack_type = 0
        self.data = ""

    @staticmethod
    def parse(text):
        packet_cmd = PacketCmd()
        dicCmd = json.loads(text)
        packet_cmd.cmd = dicCmd["Cmd"]
        packet_cmd.sub_cmd = dicCmd["SubCmd"]
        packet_cmd.packet_type = dicCmd["PacketType"]
        packet_cmd.ack_type = dicCmd["AckType"]
        packet_cmd.data = dicCmd["Data"] if "Data" in dicCmd else ""
        return packet_cmd

    def toJson(self) -> str:
        info = dict()
        info["Cmd"] = self.cmd
        info["SubCmd"] = self.sub_cmd
        info["PacketType"] = self.packet_type
        info["AckType"] = self.ack_type
        info["Data"] = self.data

        return json.dumps(info)

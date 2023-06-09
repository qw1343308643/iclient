from cmpCommand.cmd.cmpPackCmd import CmpPacketCmd
from cmpCommand.event import cmpEvent


class CmpEventPacketBinary(cmpEvent.CmpEvent):
    def __init__(self, name, packetCmd: CmpPacketCmd) -> None:
        super().__init__(name)
        self.packet_cmd = packetCmd

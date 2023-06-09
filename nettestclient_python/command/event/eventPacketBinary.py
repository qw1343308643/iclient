
import command.event.event as event
import command.cmd.binary.packetCmd as packetCmd


class EventPacketBinary(event.Event):
    def __init__(self, name, packetCmd: packetCmd.PacketCmd) -> None:
        super().__init__(name)
        self.packet_cmd = packetCmd

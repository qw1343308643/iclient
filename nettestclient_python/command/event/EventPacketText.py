
import command.event.event as event
import command.cmd.text.packetCmd as packetCmd


class EventPacketText(event.Event):
    def __init__(self, name, packetCmd: packetCmd.PacketCmd) -> None:
        super().__init__(name)
        self.packet_cmd = packetCmd

import json
from time import sleep
import command.handle.handleBase as handleBase
from command.event.EventPacketText import EventPacketText
from command.event.eventPacketBinary import EventPacketBinary
import command.cmd.define as defines
import config.config as config
from command.cmd.text.packetCmd import PacketCmd
from command.cmd.binary.packetCmd import PacketCmd as PacketCmdB
import command.cmd.text.diskMessage as diskMessage
import command.event.event as eventM
from command.interfaces.netSend import NetSend


class HandleIgnore(handleBase.HandleBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)

    def handle_default(self, event) -> bool:
        if isinstance(event, EventPacketText) and event.packet_cmd.packet_type == defines.PACKET_TYPE.PACKET_ACK.value:
            return True

        if isinstance(event, EventPacketBinary) and event.packet_cmd.packet_type == defines.PACKET_TYPE.PACKET_ACK.value:
            return True

        return False

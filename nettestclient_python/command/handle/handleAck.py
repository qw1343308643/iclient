import threading

import command.handle.handleBase as handleBase
from command.cmd.binary.cmdHeader import CmdHeader
from command.event.EventPacketText import EventPacketText
from command.event.eventPacketBinary import EventPacketBinary
import command.cmd.define as defines
from command.cmd.text.packetCmd import PacketCmd
from command.cmd.binary.packetCmd import PacketCmd as PacketCmdB
from command.interfaces.netSend import NetSend



class HandleAck(handleBase.HandleBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)
        self.ack_event = threading.Event()
        self.wait_time = 0
        self.isAck = False

    def handle_default(self, event) -> bool:
        if isinstance(event, EventPacketText) and event.packet_cmd.ack_type == defines.ACK_TYPE.ACK_ACK.value:
            cmd = PacketCmd()
            cmd.cmd = event.packet_cmd.cmd
            cmd.sub_cmd = event.packet_cmd.sub_cmd
            cmd.packet_type = defines.PACKET_TYPE.PACKET_ACK.value
            self.sendCmdText(cmd, "")
            return True

        if isinstance(event, EventPacketBinary) and event.packet_cmd.ack_type == defines.ACK_TYPE.ACK_ACK.value:
            print(f"ack node:{event.packet_cmd.cmd}, {event.packet_cmd.ack_type}, {event.packet_cmd.packet_type}")
            header = CmdHeader(None)
            cmd = PacketCmdB(header)
            cmd.cmd = event.packet_cmd.cmd
            cmd.packet_type = defines.PACKET_TYPE.PACKET_ACK.value
            self.sendCmdBytes(
                event.packet_cmd.cmd, event.packet_cmd.sub_cmd, defines.PACKET_TYPE.PACKET_ACK.value, defines.ACK_TYPE.ACK_NONE.value, None)
            return True
        return False



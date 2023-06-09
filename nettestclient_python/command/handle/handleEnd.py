import json
from time import sleep
import command.handle.handleBase as handleBase
from command.event.EventPacketText import EventPacketText
from command.event.eventPacketBinary import EventPacketBinary
import command.cmd.define as defines
from command.cmd.text.packetCmd import PacketCmd
from command.interfaces.netSend import NetSend


class HandleEnd(handleBase.HandleBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)

    def handle_default(self, event) -> bool:
        if isinstance(event, EventPacketText) and event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_GET_OFFLINE_INFO.value:
            cmd = PacketCmd()
            cmd.cmd = defines.NCMD_TYPE.NCMD_GET_OFFLINE_INFO.value
            cmd.sub_cmd = defines.NCMD_GET_OFFLINE_INFO_COMPLETE
            self.sendCmdText(cmd, "")
            return True
        return False

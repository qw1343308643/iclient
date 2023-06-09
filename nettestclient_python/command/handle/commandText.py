import threading
from command.event.EventPacketText import EventPacketText
import command.cmd.define as defines
from command.handle import commandBase
from command.interfaces.netSend import NetSend



class CommandText(commandBase.CommandBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)

    def handle_default(self, event) -> bool:
        if isinstance(event, EventPacketText) :
            # if event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_TEST_MESSAGE.value:
            print(f"test message ack:{event.packet_cmd.cmd}, {event.packet_cmd.packet_type}, {event.packet_cmd.ack_type}")
            if event.packet_cmd.cmd == self.cmd and event.packet_cmd.packet_type == self.packet_type:
                if not self.event.isSet():
                    self.event.set()
                return True
        return False
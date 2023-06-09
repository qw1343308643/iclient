import os
import command.cmd.define as defines
from command.event.eventPacketBinary import EventPacketBinary
from command.handle import commandBase
from command.interfaces.netSend import NetSend



class CommandBinary(commandBase.CommandBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)

    def handle_default(self, event) -> bool:
        if isinstance(event, EventPacketBinary):
            print(f"log packet ack:{event.packet_cmd.cmd}, {event.packet_cmd.packet_type}, {event.packet_cmd.ack_type}")
            if event.packet_cmd.cmd == self.cmd and event.packet_cmd.packet_type == self.packet_type:
                print("log event set")
                if not self.event.isSet():
                    self.event.set()
                return True
        return False
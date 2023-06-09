import abc
import command.cmd.text.packetCmd as packetCmd


class NetPacketSend(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def sendCmdText(cmd: packetCmd.PacketCmd, text: str) -> bool:
        pass

    @abc.abstractmethod
    def sendCmdBytes(cmdType: int, subCmd: int, packetType: int, ackType: int, buf: bytes) -> bool:
        pass

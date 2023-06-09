import abc
import cmd.binary.packetCmd as PacketCmd


class HandlePacketBinary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def handlePacketBinary(cmd: PacketCmd) -> bool:
        pass

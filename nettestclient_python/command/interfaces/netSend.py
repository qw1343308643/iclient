import abc


class NetSend(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def isConnect(self) -> bool:
        pass

    @abc.abstractmethod
    def sendMessage(self, text: str) -> bool:
        pass

    @abc.abstractmethod
    def sendData(self, buf: bytes) -> bool:
        pass

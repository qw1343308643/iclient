import command.interfaces.netSend as netSend

from command.handle.handleAck import HandleAck
from command.handle.handleTestMessage import HandleTestMessage
from command.handle.handleLogFile import HandleLogFile
from command.handle.handleDisk import HandleDisk
from command.handle.handleIdentity import HandleIdentify
from command.handle.handleWork import HandleWork
from command.handle.handleEnd import HandleEnd
from utility.singleton import Singleton
from work.workManage import WorkManage

class HandleFactory(Singleton):
    def __init__(self) -> None:
        super().__init__()
        self.handles = dict()

    def getHandle(self, netSend: netSend.NetSend):
        if netSend in self.handles:
            return self.handles.get(netSend)
        end = HandleEnd(None, netSend)
        work = HandleWork(end, netSend)
        identify = HandleIdentify(work, netSend)
        disk = HandleDisk(identify, netSend)
        logFile = HandleLogFile(disk, netSend)
        testMessage = HandleTestMessage(logFile, netSend)
        ack = HandleAck(testMessage, netSend)
        work_manage = WorkManage()
        work_manage.setHandles(testMessage, logFile)
        self.handles[netSend] = ack
        return ack

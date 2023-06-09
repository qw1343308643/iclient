import threading

from cmpClientHandle.cmdClientHandleEnd import CmpClientHandleEnd
from cmpClientHandle.cmdClientHandleWork import CmpClientHandleWork
from cmpClientHandle.cmpClientHandleLog import CmpClientHandleLog
from cmpClientHandle.cmpClientHandleTestStatus import CmpClientHandleTestStatus
from cmpClientHandle.cmdClientHandleWorkType import CmpClientHandleWorkType
from cmpClientHandle.cmdClientHandleAddDisk import CmpClientHandleAddDisk
from cmpClientHandle.cmdClientHandleInitInfo import CmpClientHandleInitInfo
from cmpUtility.singleton import Singleton


class ClientHandleFactory(Singleton):
    _LOCK = threading.Lock()
    def __init__(self) -> None:
        super().__init__()
        self.handles = dict()

    def getHandle(self, cmp):
        self._LOCK.acquire()
        if cmp in self.handles:
            self._LOCK.release()
            return self.handles.get(cmp)
        end = CmpClientHandleEnd(None, cmp)
        work = CmpClientHandleWork(end, cmp)
        log = CmpClientHandleLog(work, cmp)
        testStatus = CmpClientHandleTestStatus(log, cmp)  # 测试状态
        workType = CmpClientHandleWorkType(testStatus, cmp)
        addDisk = CmpClientHandleAddDisk(workType, cmp)
        initInfo = CmpClientHandleInitInfo(addDisk, cmp)
        self.handles[cmp] = initInfo
        self._LOCK.release()
        return initInfo
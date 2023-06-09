import threading

from cmpServerHandle.cmdHandleEnd import CmpHandleEnd
from cmpServerHandle.cmpHandleDisk import CmpHandleDisk
from cmpServerHandle.cmpHandleLog import CmpHandleLog
from cmpServerHandle.cmpHandleTestName import CmpHandleTestName
from cmpServerHandle.cmpHandleTestSetting import CmpHandleTestSetting
from cmpServerHandle.cmpHandleTestStatus import CmpHandleTestStatus
from cmpServerHandle.cmpHandleWork import CmpHandleWork
from cmpServerHandle.cmpHandleInitInfo import CmpHandleInitInfo
from cmpUtility.singleton import Singleton


class HandleFactory(Singleton):
    _LOCK = threading.Lock()
    def __init__(self) -> None:
        super().__init__()
        self.handles = dict()

    def getHandle(self, cmp):
        self._LOCK.acquire()
        if cmp in self.handles:
            self._LOCK.release()
            return self.handles.get(cmp)
        end = CmpHandleEnd(None, cmp)  # 结束
        log = CmpHandleLog(end, cmp)  # 获取日志
        work = CmpHandleWork(log, cmp)  # 测试任务管理
        testSetting = CmpHandleTestSetting(work, cmp)  # 测试配置内容
        testName = CmpHandleTestName(testSetting, cmp)  # 测试工具名称
        disk = CmpHandleDisk(testName, cmp)  # 磁盘信息
        testStatus = CmpHandleTestStatus(disk, cmp)  # 测试状态
        initInfo = CmpHandleInitInfo(testStatus, cmp)

        self.handles[cmp] = initInfo
        self._LOCK.release()
        return initInfo
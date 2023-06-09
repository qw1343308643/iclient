import time

import cmp
from datetime import datetime
import threading

workType = "python test"

class WorkTest(object):
    _nItem = 0
    _strDevice = ""
    _bRun = False
    _bFinished = False
    _strLogDir = ""
    _strConfigFile = ""
    _tBeginTime = datetime.now()
    _tEndTime = None
    _nErrorTimes = 0
    _nCurrentCycles = 0
    _strStatus = ""
    _bStop = False
    _logFile = None
    _logPath = ""
    _testname=""
    _itemList=[]
    _TotalPos = 0
    _CurrentPos = 0


    # 根据配置文件，识别配置内容
    def InitParam(self):
        return True

    # 初始化日志
    def InitLogFile(self):
        if self._logFile is not None:
            self._logFile.close()
        return True

    def PrepareForWork(self, nItem: int, strDevice: str, strLogDir: str, strConfigFile: str)->bool:
        self._bRun = True
        self._bFinished = False
        self._strDevice = strDevice
        self._strLogDir = strLogDir
        self._strConfigFile = strConfigFile
        self._tBeginTime = datetime.now()

        if strDevice == False:
            self._nErrorTimes += 1
            return False
        if not self.InitParam():
            self._nErrorTimes += 1
            return False
        if not self.InitLogFile():
            self._nErrorTimes += 1
            return False
        return True

    def EndWork(self):
        self.__tEndTime = datetime.now()
        if self._logFile is not None:
            self._logFile.close()

    def ExitWork(self):
        self._bRun = False
        self._bFinished = True

    def StopWork(self):
        self._bStop = True
        self._bFinished = True

    def ToDoWork(self):
        self._TotalPos = 120
        for _ in range(self._TotalPos):
            if not self._bStop and not self._bFinished:
                self._nCurrentCycles += 1
                time.sleep(1)

    def GetStatus(self)->cmp.CMPDeviceStatus:
        elapseTime = datetime.now() - self._tBeginTime
        hours = elapseTime.seconds // (60 * 60)
        minutes = elapseTime.seconds % (60 * 60) // 60
        seconds = elapseTime.seconds % (60 * 60) % 60
        strTime = str(hours) + " h " + str(minutes) + \
            " m " + str(seconds) + " s"
        cmpStatus = cmp.CMPDeviceStatus()
        cmpStatus.CurrentCycles = self._nCurrentCycles
        cmpStatus.TotalPos = self._TotalPos
        cmpStatus.CurrentPos = self._nCurrentCycles
        cmpStatus.Finished = self._bFinished
        cmpStatus.Run = self._bRun
        cmpStatus.Status = self._strStatus
        cmpStatus.ErrorTimes = self._nErrorTimes
        cmpStatus.WorkType = workType
        cmpStatus.ExtraInfo["Duration"] = strTime

        # 模拟一些额外状态信息
        # for j in range(4):
        #     randomValue = ""
        #     for k in range(20):
        #         randomValue += str(random.randint(0, 20))
        #     cmpStatus.ExtraInfo['random' + str(j)] = randomValue

        return cmpStatus

    def GetLogPath(self):
        return self._logPath


class MyCMPClinet(cmp.CMPClient):
    _work = None
    _doneEvent = threading.Event()
    _workThread = None
    _workThreadList = {}

    def WaitForDone(self):
        self._doneEvent.wait()

    def CMPAddDisk(self, strDevice: str, nItem: int)->bool:
        self._strDevice = strDevice
        self._nItem = nItem
        return True

    def CMPPreStart(self, strLogDir: str, strConfigPath: str) ->bool:
        self._strLogDir = strLogDir
        self._strConfigPath = strConfigPath
        strConfigs = strConfigPath.split("\n")
        for config in strConfigs:
            if config.endswith(".ini"):
                _strConfigPath = config
                return True  # 可根据实际情况，识别适合本工具的配置，此处假定任何ini文件都适合
        return False

    def CMPGetTestType(self)->[bool, cmp.CMP_TEST_TYPE]:
        return True, cmp.CMP_TEST_TYPE.TEST_TYPE_CYCLE

    def _StartTest(self):
        self._work = WorkTest()
        print("---当前盘的名称---:",self._strDevice)
        if not self._work.PrepareForWork(self._nItem, self._strDevice, self._strLogDir, self._strConfigPath):
            return False
        if self._work.ToDoWork(self):
            self._work.EndWork()
        self._work.ExitWork()
        self._doneEvent.set()
        return True


    def CMPStartTest(self, nItem: int)->bool:
        self._workThread = threading.Thread(target=ThreadRun, args=(self,))
        self._workThread.start()
        return True


    def CMPStopTest(self, nItem: int):
        if self._work is not None:
            self.NotifyReboot(True)
            self._work.StopWork()

    def CMPGetStatus(self, nItem: int)->cmp.CMPDeviceStatus:
        if self._work is not None:
            return self._work.GetStatus()
        return cmp.CMPDeviceStatus()

    def CMPGetLogs(self, nItem: int)->str:
        if self._work is not None:
            return self._work.GetLogPath()
        return ""

    def CMPGetCustomInfo(self, InfoType: int):
        if InfoType == cmp.CMP_INFO_TYPE.INFO_WORK_STR.value:
            return workType  # 返回本工作可识别的字符串，如BurnIn、H2test等
        elif InfoType == cmp.CMP_INFO_TYPE.INFO_PORT_NUMBER.value:
            return 1  # 一拖一程序返回1，如支持一拖多，请返回实际能测试的最大端口数
        return 0


def ThreadRun(myCMPClinet: MyCMPClinet):
    myCMPClinet._StartTest()


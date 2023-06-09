from enum import Enum
import sys
import os
dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
cmpLibPath = os.path.join(dirname, "cmpLib")
sys.path.append(cmpLibPath)
import cmpp


class CCMPClientContext(object):
    def __init__(self, contextp):
        self._contextp = contextp
    '''
    获取当前项目名称
    返回值
        str 项目名
    '''

    def GetFlowName(self):
        return self._contextp.GetFlowName()

    '''
    获取当前项目总步骤数
    返回值
        int:总步骤数
    '''

    def GetTotalSteps(self):
        return self._contextp.GetTotalSteps()

    '''
    获取指定步骤的工具数
    参数
        stepIndex
            int:以1开始的步骤序号
    返回值
        int: 指定步骤的工具数，0表示出错
    '''

    def GetTotalTools(self, stepIndex: int):
        return self._contextp.GetTotalTools(stepIndex)

    '''
    获取指定步骤的指定工具的名称
    参数
        stepIndex
            int:以1开始的步骤序号
        toolIndex
            int:以1开始的工具序号
    返回值  
        str 工具名
    '''

    def GetToolName(self, stepIndex: int, toolIndex: int):
        return self._contextp.GetToolName(stepIndex, toolIndex)

    '''
    获取当前步骤序号
    返回值
        int:以1开始的步骤序号，0表示出错
    '''

    def GetCurrentStepIndex(self):
        return self._contextp.GetCurrentStepIndex()

    '''
    获取当前工具序号
    返回值
        int:以1开始的工具序号，0表示出错
    '''

    def GetCurrentToolIndex(self):
        return self._contextp.GetCurrentToolIndex()


class CMPDeviceStatus(object):
    CurrentCycles = 0  # 当前测试次数
    ErrorTimes = 0  # 当前错误次数
    ErrorCode = 0  # 错误代码
    CurrentPos = 0  # 当前进度
    TotalPos = 0  # 总进度
    Run = False  # 测试是否正在运行
    Finished = False  # 测试是否完成
    WorkType = ""  # 工作类型字符串，如BurnIn,h2test
    Speed = ""  # 当前磁盘的读写速度
    Status = ""  # 当前测试状态
    ExtraInfo = {}  # 额外测试信息,字典类型，key与value必须为字符串


class CMP_INFO_TYPE(Enum):
    INFO_WORK_STR = 0  # 工作类型,字符串
    INFO_PORT_NUMBER = 1  # 端口总数,返回>1的数，则认为其支持一拖多，测试不同的盘，只启动测试程序一次。否则启动多次


class CMP_TEST_TYPE(Enum):
    TEST_TYPE_NONE = 0  # 测试类型为无，表示不支持继续测试
    TEST_TYPE_TIME = 1  # 测试类型为时间，表示继续测试时新的测试时间为总时间 -  已测时间
    TEST_TYPE_CYCLE = 2  # 测试类型为次数，表示继续测试时新的测试次数为总次数 - 已测次数


class CMPClient(object):
    _strDevice = ""
    _nItem = 0
    _strLogDir = ""
    _strConfigPath = ""
    _cmpClientProxy = None
    _cmpClientContextProxy = None

    '''
    初始化CMP环境，如是在分布式环境下测试时，则返回成功。此函数应最先调用
    mainFilePath
        入口文件的绝对路径
    '''

    def InitCMP(self, mainFilePath)->bool:
        self._cmpClientProxy = cmpp.CCMPClientProxy()
        return self._cmpClientProxy.Init(self, mainFilePath)

    def CMPGetClientContext(self):
        if self._cmpClientProxy is None:
            return None
        if self._cmpClientContextProxy is not None:
            return self._cmpClientContextProxy
        self._cmpClientContextProxy = CCMPClientContext(
            self._cmpClientProxy.GetClientContext())
        return self._cmpClientContextProxy

    '''
    磁盘定位，支持一拖多的测试程序，此调用可能会调用多次（<= 端口总数）
    参数
        strDevice,字符串类型
            windows中strDevice[0]如小于A则为物理盘，大于等于A则为逻辑盘
            linux中则为类似/dev/sda / dev/sda1
        nItem,整数类型
            当前盘对应的端口号，一次测试过程中，端口号固定不变，而磁盘有可能改变
    返回值 
        bool 
            返回失败后，则不再继续,其后紧跟CMPGetStatus调用，获取详细出错信息
    '''

    def CMPAddDisk(self, strDevice: str, nItem: int)->bool:
        self._strDevice = strDevice
        self._nItem = nItem
        return True

    '''
    预开始测试，主要进行测试的一些初始化。一拖多程序只支持一个配置测试，因此此调用只会调用一次，没有nItem参数
    参数
        strLogDir,字符串类型
            日志存放目录，方便统一存放
        strConfigPath，字符串类型
            当前测试的配置,多个配置以\n分隔
    返回值 
        bool 
            返回失败后，则不再继续，其后紧跟CMPGetStatus调用，获取详细出错信息
    '''

    def CMPPreStart(self, strLogDir: str, strConfigPath: str) ->bool:
        self._strLogDir = strLogDir
        self._strConfigPath = strConfigPath
        strConfigs = strConfigPath.split("\n")
        for config in strConfigs:
            if config.endswith(".ini"):
                _strConfigPath = config
                return True  # 可根据实际情况，识别适合本工具的配置，此处假定任何ini文件都适合
        return False
    '''
    获取测试的类型,一定会在CMPPreStart后发送。测试程序根据前面设置的配置路径来判断
	一般会在异常重启后继续测试时发送,调用端根据此值来决定是否能继续测试
    返回值
      bool
        false表示遇到错误不再继续，其后紧跟CMPGetStatus调用，获取详细出错信息
      CMP_TEST_TYPE
        实际的测试类型
	'''

    def CMPGetTestType(self)->[bool, CMP_TEST_TYPE]:
        return True, CMP_TEST_TYPE.TEST_TYPE_CYCLE

    '''
    开始测试
    参数
        nItem
            端口号
    返回值
        bool
            false表示遇到错误不再继续，其后紧跟CMPGetStatus调用，获取详细出错信息
    '''

    def CMPStartTest(self, nItem: int)->bool:
        return True

    '''
    开始测试
	此调用一般会在继续测试时调用,表示按设定的配置测试,但配置中的
	测试次数要更新为 总次数 - 已测次数，
	或测试时间要更新为 总时间 - 已测时间
    '''

    def CMPContinueTest(self, nItem: int, testedSeconds: int, testedCycles: int)->bool:
        return True
    '''
    停止测试
    参数
        nItem
            端口号
    返回值
        无
    '''

    def CMPStopTest(self, nItem: int)->bool:
        return True
    '''
    获取状态，会不定时调用,当以上函数有返回False时，一般紧跟此调用获取出错信息
    参数
        nItem
	        当前端口号
	返回值
        CMPDeviceStatus
	        当前所有测试信息
    '''

    def CMPGetStatus(self, nItem: int)->CMPDeviceStatus:
        return CMPDeviceStatus()

    '''
    获取测试日志，在测试完成时调用
    参数
        nItem
	        当前端口号
	返回值
        str
            为日志的绝对路径，多个日志路径以\n分隔
    '''

    def CMPGetLogs(self, nItem: int)->str:
        return ""

    '''
    获取其他信息
    参数
        InfoType
	        获取信息的类别
	返回值
        根据InfoType类型的不同而返回值不同
    '''

    def CMPGetCustomInfo(self, InfoType: int):
        if InfoType == CMP_INFO_TYPE.INFO_WORK_STR.value:
            return ""  # 返回本工作可识别的字符串，如BurnIn、H2test等
        elif InfoType == CMP_INFO_TYPE.INFO_PORT_NUMBER.value:
            return 1  # 一拖一程序返回1，如支持一拖多，请返回实际能测试的最大端口数
        return 0

    def NotifyReboot(self, clean=False):
        if self._cmpClientProxy is not None:
            self._cmpClientProxy.NotifyReboot(clean)

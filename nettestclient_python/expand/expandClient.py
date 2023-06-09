import importlib
import inspect
import os
import sys


class MainTest:
    sendStatus = (22, 0, 0, 0)
    sendLog = (14, 0, 0, 0)
    sendStopTest = (20, 0, 0, 0)  # 主动停止测试任务
    releaseTask = (0, 0, 3, 0)  # 释放资源
    errorDict = {"Good": 0, "Error": 0, "Warning": 2}
    UC = (
        (0, 0, 1, 0),   # 告诉客户端不需要重启
        (0, 0, 1, 1),   # 重启前通知客户端要重启
        (0, 0, 2, 1),   # 返回服务器程序文件所在目录
        (0, 0, 3, 1),   # 返回配置文件
        (38, 0, 0, 0),  # 序列号
        (39, 0, 0, 0),  # 刷新测试时间
        (20, 0, 0, 0)   # 停止测试
    )
    TestMessageData = {
        "PhyUSBPort": "",
        "Total": "",
        "Current": "",
        "PASS": "",
        "Fail": "",
        "Warning": "",
        "SpaceUsed": "",
    }

    def __init__(self, tool):
        self.getConfigRsp = tool.workParam["Config"]
        # test message
        self.total = 0
        self.current = 0
        self.passed = 0
        self.failed = 0
        self.warning = 0
        self.used = 0
        self.pyhPort = 'None'
        self.comment= 'None'
        self.runTime = 0
        self.bFinish = False
        self.bRun = True
        self.errorState = 0
        self.tool = 0
        self.nContinue = 1

    def run(self):
        path = r"D:\BackupFiles\yufeng.lu\Desktop\pytool\SubTest.py"
        sys.path.insert(0, os.path.dirname(path))
        modName = os.path.basename(path).split(".")[0]
        if modName in sys.modules:
            del sys.modules[modName]
        impMod = importlib.import_module(modName)
        for atttName, cls in inspect.getmembers(impMod, inspect.isclass):
            if atttName.lower() == "subtest":
                attrType = type("" + atttName, (cls,), dict())
                t = attrType(1, 2, 3)
                ret = t.run()

    def toolLogger(self, message=None, status=True, changeStaste=None,
                   arg=None, waitRsp=True):
        if isinstance(message, tuple):
            if message in self.UC:
                if message == (0, 0, 2, 1):
                    return os.path.abspath(os.path.dirname(__file__))
                elif message == (0, 0, 3, 1):
                    return self.getConfigRsp
                elif message == (39, 0, 0, 0):
                    pass

        if isinstance(changeStaste, dict):
            for key, val in changeStaste.items():
                if key == "PhyUSBPort":
                    self.pyhPort = str(val)
                elif key == 'Total' and isinstance(val, int):
                    self.total = val






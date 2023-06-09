import logging
import os
import random
import threading
import time
from datetime import datetime

from common.deviceStatus import DeviceStatus
from config import config


class Work:

    def __init__(self, workConfig, tool, onSetStatus, getSelfStatus, onSetDeviceLog, host):
        # 任务运行状态
        self.DiskNumber = ""
        self.PortNumber = 0
        self.WorkConfig = workConfig
        self.Run = True
        self.Stop = False
        self.Finished = False
        self.StartTime = None
        self.EndTime = None
        self.Error_times = 0
        self.ErrorCode = 0
        self.IntervalMin = 5 * 60
        self.IntervalMax = 6 * 60
        self.Result = "PASS"
        # 测试信息
        self.step = None
        self.tool = tool
        self.onSetStatus = onSetStatus
        self.getSelfStatus = getSelfStatus
        self.onSetDeviceLog = onSetDeviceLog

        self.logger = None
        self.config = config.Config()
        # log刷新定时器
        self.logPreshTask = PreshServerLog()


    def startWork(self, step):
        self.step = step
        self.DiskNumber = self.WorkConfig.disk_message.device
        self.PortNumber = self.WorkConfig.disk_message.index
        self.TodoWork()
        return

    def TodoWork(self):
        # try:
            if self.Finished or self.Stop:
                return
            status = DeviceStatus()
            status.tool_id = self.tool.tool_id
            status.run = True
            status.finished = False
            status.status = "Testing..."
            self.onSetStatus(self.DiskNumber, self.PortNumber, status)

            # 不按停止就一直循环测试
            self.StartTime = datetime.now()
            logPath = os.path.join(self.config.settings["LogPath"], f"{self.DiskNumber}_{self.PortNumber}_{time.strftime('%Y%m%d_%H%M%S', time.localtime())}.log").replace("\\", os.sep)
            self.initLog(logPath)
            self.logPreshTask.setAttr(self.DiskNumber, self.PortNumber, self.tool.tool_id, self.logger, self.StartTime, self.onSetStatus, self.closeLog)
            logPreshTimer = threading.Timer(1, self.logPreshTask.run)
            logPreshTimer.start()
            while not self.Stop:
                time.sleep(10)
            self.logPreshTask.flag = False
            self.EndTime = datetime.now()
            self.onSetDeviceLog(self.DiskNumber, self.PortNumber, self.tool.tool_id, logPath)  # 上传测试日志

            status.status = "PASS"
            if self.Error_times > 0:
                self.status = "fail"
                self.Result = "Fail"
            elif self.Stop == True:
                self.status = "stop"
                self.Result = "Stop"
            status.run = False
            status.finished = True
            self.onSetStatus(self.DiskNumber, self.PortNumber, status)
            if self.tool.main_tool:
                for taskWork in self.step:
                    taskWork.Run = False
                    taskWork.Finished = True
            return
        # except Exception as e:
        #     print(f"任务执行报错:{e}")

    # 初始化生成工具log
    def initLog(self, path: str):
        self.logger = logging.getLogger(f"LogApp_{self.DiskNumber}_{time.strftime('%Y%m%d_%H%M%S', time.localtime())}")
        # 指定logger输出格式
        formatter = logging.Formatter('%(message)s')
        # 文件日志
        self.file_handler = logging.FileHandler(path)
        self.file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.INFO)
        self.createLogHeader()

    # 创建log头部内容
    def createLogHeader(self):
        self.logger.info("!#log")
        self.logger.info(f"Python Client Test:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        self.logger.info(f"DiskNumber:{self.DiskNumber}")
        self.logger.info(f"PortNumber:{self.PortNumber}")

    def closeLog(self):
        try:
            self.file_handler.close()
        except:
            pass

# 日志刷新定时器
class PreshServerLog:
    def __init__(self, DiskNumber=None, PortNumber=None, tool_id=None, logger=None, StartTime=None, callback=None, close_callback=None):
        self.flag = True
        self.IntervalTime = random.randint(5 * 50, 6 * 60)
        self.isWaitFresh = True

        self.DiskNumber = DiskNumber
        self.PortNumber = PortNumber
        self.tool_id = tool_id
        self.logger = logger
        self.StartTime = StartTime
        self.onSetStatus = callback
        self.close_callback = close_callback

    def setAttr(self, DiskNumber, PortNumber, tool_id, logger, StartTime, callback, close_callback):
        self.DiskNumber = DiskNumber
        self.PortNumber = PortNumber
        self.tool_id = tool_id
        self.logger = logger
        self.StartTime = StartTime
        self.onSetStatus = callback
        self.close_callback = close_callback

    def run(self):
        try:
            logRandomTime = random.randint(10, 15)
            sys_time_count = 0
            server_time_count = 0
            while self.flag:
                time.sleep(1)
                sys_time_count += 1
                server_time_count += 1
                if sys_time_count >= logRandomTime:
                    self.preshLog(isSend=False)
                    sys_time_count = 0
                    logRandomTime = random.randint(10, 15)
                if server_time_count >= self.IntervalTime:
                    self.preshLog(isSend=True)
                    server_time_count = 0
            self.preshLog(isSend=True)  # 最后一次刷新上传服务器
            self.close_callback()
            return
        except Exception as e:
            print(f"log定时器报错:{e}")

    def preshLog(self, isSend=False):
        status = DeviceStatus()
        status.tool_id = self.tool_id
        status.run = True
        status.finished = False
        status.status = "Testing..."
        for j in range(4):
            randomValue = ""
            for k in range(20):
                for x in range(2):
                    randomValue += str(random.randint(0, 9))
                randomValue += ","
            state = {'Key': 'random' + str(j), 'Value': randomValue}
            status.addStatus(state)
            info = f"{str(state['Key'])}:{state['Value']}"
            self.logger.info(info)
        elapseTime = datetime.now() - self.StartTime
        hours = elapseTime.seconds // (60 * 60)
        minutes = elapseTime.seconds % (60 * 60) // 60
        seconds = elapseTime.seconds % (60 * 60) % 60
        strTime = str(hours) + " h " + str(minutes) + \
                  " m " + str(seconds) + " s"
        Duration = {'Key': 'Duration', 'Value': strTime}
        status.addStatus(Duration)
        info = f"{str(Duration['Key'])}:{Duration['Value']}"
        self.logger.info(info)
        if isSend:
            self.onSetStatus(self.DiskNumber, self.PortNumber, status)

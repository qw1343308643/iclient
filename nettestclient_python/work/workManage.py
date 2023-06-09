import copy
import os
import pickle
import sys

import threading
import time
import uuid
from datetime import datetime
from queue import Queue

from command.cmd.text.workConfigMessage import WorkConfigMessage
from command.cmd.text.diskPortMessage import DiskPortMessage
from command.handle.handleIdentity import HandleIdentify
from command.handle.handleTestMessage import HandleTestMessage
from command.handle.handleLogFile import HandleLogFile
from common.deviceStatus import DeviceStatus
from common.ledControl import LedControl
from common.lostWorkConfigMessage import LostWorkConfigMessage
from config.errorCode import *
from config.config import Config
from config.templete import log_result_templete, log_header_templete
from work.downloadWork import DownLoadWork
from work.workTest import Work

class WorkManage():
    #

    def __init__(self, netsend=None):
        self.netSend = netsend
        if not hasattr(WorkManage, "_first_init"):
            WorkManage._first_init = True
            self.configSetting = Config()
            self._handle_test_message = None
            self._handel_log_file = None
            self.diskWork = {}
            self.diskResult = {}
            self.diskStepWork = {}
            self.index_port = 5000
            self.runThreads = {}
            self._LOCK = threading.Lock()


    def __new__(cls, *args, **kwargs):
        if not hasattr(WorkManage, "_instance"):
            WorkManage._instance = object.__new__(cls)
        return WorkManage._instance

    def setHandles(self, handleTestMessage: HandleTestMessage, handleLogFile: HandleLogFile):
        self._handle_test_message = handleTestMessage
        self._handel_log_file = handleLogFile

    @staticmethod
    def isDiskExist(device: str):
        # if not os.path.ex
        return True

    def startTest(self, netSend, data):
        print("---start Test---")
        status_id = 0
        try:
            workConfigMessage = WorkConfigMessage.parse(data)
            status_id = workConfigMessage.status_id
            status = DeviceStatus()
            status.status_id = status_id
            device = workConfigMessage.disk_message.device
            index = workConfigMessage.disk_message.index
        except Exception as e:
            workConfigMessage = WorkConfigMessage.parse(data, ignore=True)
            device = workConfigMessage.disk_message.device
            index = workConfigMessage.disk_message.index
            self.endWork(device, index, status=str(e), error_times=1, type_name="server data error", status_id=status_id)
            return
        self.configSetting.load()
        python_exe = self.configSetting.settings["python"]
        error_type = workConfigMessage.error_type
        error_times = 0
        works = []
        self.diskWork[index] = works
        self.diskResult[index] = "PASS"
        print("send Initializing")
        status = self.getSelfStatus(device, index, "Initializing...", 0, 0, status)
        self.onSetStatus(device, index, status)
        # 检测盘是否存在
        if not self.isDiskExist(workConfigMessage.disk_message.device):
            self.getSelfStatus(device, index, status, ERROR_CODE_STATUS.STATUS_CLIENT.value,
                               ERROR_CODE_ERROR.NO_CARD.value, status)
            self.onSetStatus(device, index, status)
            self.endWork(device, index, status=str(ERROR_CODE_ERROR.NO_CARD.value), error_times=1, type_name="no exist device",
                         status_id=status_id)
            return
        # 遍历下载任务工具
        print("start download tool")
        status = self.getSelfStatus(device, index, "downLoad tool...", 0, 0, status)
        self.onSetStatus(device, index, status)
        # self._LOCK.acquire()
        with self._LOCK:
            try:
                for step in workConfigMessage.step_configs:
                    for tool in step.tools:
                        taskWork = DownLoadWork(workConfigMessage, tool, netSend, self.onSetStatus)
                        meesage = taskWork.download()
                        if meesage["flag"] == False:
                            self.endWork(device, index, status=meesage["status"], error_times=1, type_name="download work error", status_id=status_id)
                            return
            except Exception as e:
                print(e)
                self.endWork(device, index, status=str(e), error_times=1, type_name="download work error", status_id=status_id)
                return
            # finally:
            #     self._LOCK.release()
        print("download finish")
        # 下载完成
        status = self.getSelfStatus(device, index, "就绪", 0, 0, status)
        self.onSetStatus(device, index, status)
        # 添加步骤任务
        try:
            for step in workConfigMessage.step_configs:
                stepList = []
                for tool in step.tools:
                    taskWork = Work(workConfigMessage, tool)
                    stepList.append(taskWork)
                works.append(stepList)
        except NetTestClientError as e:
            print(e)
            return self.endWork(device, index, status=str(e), error_times=1, type_name="Work Ana NetTestClientError", status_id=status_id)
        except Exception as e:
            print(e)
            return self.endWork(device, index, status=str(e), error_times=1, type_name="Work Ana Exception", status_id=status_id)
        # 保存测试任务信息
        lostTestStatus = LostWorkConfigMessage()
        lostTestStatus.lostWorkConfigMessageDict[index] = works
        lostTestStatus.workConfigMessageDict[index] = workConfigMessage
        # 执行步骤任务
        startTime = datetime.now()
        lostTestStatus.startTimeDict[index] = startTime
        end_status = ""
        dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
        path = os.path.join(dirname, "cmpLib")
        sys.path.append(path)
        from cmpClientWork import CMPClientWork
        LedControl.testing()
        status = self.getSelfStatus(device, index, "testing...", 0, 0, status)
        self.onSetStatus(device, index, status)
        try:
            for step in works:
                stepIndex = 1
                stepWork = {}
                self.diskStepWork[index] = stepWork
                for tool in step:
                    toolIndex= 1
                    if tool.run:
                        # tool: 工具信息
                        # cmd_queue: 命令队列
                        # onSetStatus: 发送测试消息回调函数
                        # onSetDeviceLog: 发送测试log回调函数
                        # updateNotifyLostWorkConfig 重启回调函数
                        # DeviceStatus: 测试信息结构类
                        with self._LOCK:
                            cmd_queue = Queue()
                            self.index_port += 1
                            port = copy.copy(self.index_port)
                            # port = self.checkPortUse(port)
                            # self.index_port = port
                            print(f"index:{index}, port:{port}")
                            cmp = CMPClientWork(tool, cmd_queue, self.onSetStatus, self.onSetDeviceLog, self.updateNotifyLostWorkConfig, DeviceStatus, port,
                                                workConfigMessage, self.runThreads, python_exe)
                            ret = cmp.startTest()
                        # self._LOCK.release()
                        if not ret["result"]:
                            LedControl.testStepFail()
                            raise NetTestClientError(ERROR_CODE_ERROR.CONNECT_TOOL_FAIL.value)
                        task = threading.Thread(target=cmp.run, name=f"clientCMP{uuid.uuid4()}")
                        task.start()
                        stepWork[cmp] = task
                    toolIndex += 1
                while self.diskStepWork[index]:
                    for cmp in list(self.diskStepWork[index].keys()):
                        task = self.diskStepWork[index][cmp]
                        time.sleep(1)
                        if not task.is_alive() and "clientCMP" in task.name:
                            self.diskStepWork[index].pop(cmp)
                            print("cmp.tool.run:",cmp.tool.run)
                            print("cmp.tool.isReboot:",cmp.tool.isReboot)
                            if cmp.tool.run:  # 判断工具是否是正常结束
                                if cmp.tool.isReboot:
                                    print("wait reboot")
                                    time.sleep(600)
                                    ret = {"result": False, "message": "got reboot cmd but did not reboot"}
                                    raise NetTestClientError(ERROR_CODE_ERROR.ABNORMAL_END.value)
                                print("tool false exit")
                                ret = {"result": False, "message": "abnormal end of tool"}
                                raise NetTestClientError(ERROR_CODE_ERROR.ABNORMAL_END.value)
                            if cmp.tool.workParam["MainTool"] == True:  # 判断是否存在主副工具
                                for cmp, task in self.diskStepWork[index].items():
                                    cmp.cmd_pipe.put((3, 0, 0, 0))  # 向副工具发送停止命令
                            if cmp.tool.error_flag and error_type == 1:  # 判断是否有error和是否要继续运行
                                error_times += 1
                    if error_times >= 1:
                        break
                if error_times >= 1:
                    break
                stepIndex += 1
        except NetTestClientError:
            LedControl.testFail()
            end_status = ret["message"]
            error_times += 1
        except Exception as e:
            LedControl.testFail()
            end_status = str(e)
            error_times += 1

        self.getResult(device)  # 获取整个流程的运行结果 PASS STOP FAIL
        if error_times == 0:
            LedControl.testPass()
        endTime = datetime.now()
        headerValues = self.getHeaderArgs(workConfigMessage, str(startTime.strftime("%Y-%m-%d %H:%M:%S")),
                                          str(endTime.strftime("%Y-%m-%d %H:%M:%S")), len(works))
        logPath = self.createTestLog(works, headerValues, device, index)
        self.endWork(device, index, status=end_status, error_times=error_times, type_name="end status",
                     status_id=status_id)  # 发送结束状态
        # 上传日志
        self.onSetDeviceLog(device,index, status_id, logPath)


    # 继续测试
    def continueTest(self, workConfigMessage, works, startTime):
        device = workConfigMessage.disk_message.device
        index = workConfigMessage.disk_message.index
        try:
            status_id = workConfigMessage.status_id
        except:
            status_id = 0
        error_type = workConfigMessage.error_type
        error_times = 0
        self.diskWork[index] = works
        self.diskResult[index] = "PASS"

        # 保存测试任务信息
        lostTestStatus = LostWorkConfigMessage()
        lostTestStatus.lostWorkConfigMessageDict[index] = works
        lostTestStatus.workConfigMessageDict[index] = workConfigMessage
        # 执行步骤任务
        lostTestStatus.startTimeDict[index] = startTime
        end_status = ""
        dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
        path = os.path.join(dirname, "cmpLib")
        sys.path.append(path)
        from cmpClientWork import CMPClientWork
        LedControl.testing()

        try:
            for step in works:
                stepIndex = 1
                stepWork = {}
                self.diskStepWork[index] = stepWork
                for tool in step:
                    toolIndex = 1
                    if tool.run:
                        # tool: 工具信息
                        # cmd_queue: 命令队列
                        # onSetStatus: 发送测试消息回调函数
                        # onSetDeviceLog: 发送测试log回调函数
                        # updateNotifyLostWorkConfig 重启回调函数
                        # DeviceStatus: 测试信息结构类
                        with self._LOCK:
                            cmd_queue = Queue()
                            self.index_port += 1
                            port = copy.copy(self.index_port)
                            port = self.checkPortUse(port)
                            self.index_port = port
                            print(tool.workParam["ToolID"])
                            cmp = CMPClientWork(tool, cmd_queue, self.onSetStatus, self.onSetDeviceLog,
                                                self.updateNotifyLostWorkConfig, DeviceStatus, port,
                                                workConfigMessage, self.runThreads, self.configSetting.settings["python"])
                            ret = cmp.startTest()
                        if not ret["result"]:
                            LedControl.testStepFail()
                            raise NetTestClientError(ERROR_CODE_ERROR.CONNECT_TOOL_FAIL.value)
                        task = threading.Thread(target=cmp.run, name=f"clientCMP{uuid.uuid4()}")
                        task.start()
                        stepWork[cmp] = task
                    toolIndex += 1
                while self.diskStepWork[index]:
                    for cmp in list(self.diskStepWork[index].keys()):
                        task = self.diskStepWork[index][cmp]
                        time.sleep(1)
                        if not task.is_alive() and "clientCMP" in task.name:
                            self.diskStepWork[index].pop(cmp)
                            # if cmp.tool.run:  # 判断工具是否是正常结束
                            #     ret = {"result": False, "message": "abnormal end of tool"}
                            #     raise NetTestClientError(ERROR_CODE_ERROR.ABNORMAL_END.value)
                            #     pass
                            if cmp.tool.workParam["MainTool"] == True:  # 判断是否存在主副工具
                                for cmp, task in self.diskStepWork[index].items():
                                    cmp.cmd_pipe.put((3, 0, 0, 0))  # 向副工具发送停止命令
                            if cmp.tool.error_flag and error_type == 1:  # 判断是否有error和是否要继续运行
                                error_times += 1
                    if error_times >= 1:
                        break
                    time.sleep(30)
                stepIndex += 1
        except NetTestClientError:
            LedControl.testFail()
            end_status = ret["message"]
            error_times += 1
        except Exception as e:
            LedControl.testFail()
            end_status = str(e)
            error_times += 1
        self.getResult(device)  # 获取整个流程的运行结果 PASS STOP FAIL
        if error_times == 0:
            LedControl.testPass()
        endTime = datetime.now()
        headerValues = self.getHeaderArgs(workConfigMessage, str(startTime.strftime("%Y-%m-%d %H:%M:%S")),
                                          str(endTime.strftime("%Y-%m-%d %H:%M:%S")), len(works))
        logPath = self.createTestLog(works, headerValues, device, index)
        self.endWork(device, index, status=end_status, error_times=error_times, type_name="end status",
                     status_id=status_id)  # 发送结束状态
        # 上传日志
        self.onSetDeviceLog(device, index, status_id, logPath)
        # 清空任务管理器对应的内容


    def stopWork(self, disk: DiskPortMessage) -> bool:
        works = self.diskWork.get(disk.index)
        if works:
            for stepList in works:
                for work in stepList:
                    work.run = False
            for cmp in self.diskStepWork[disk.index].keys():
                cmp.cmd_pipe.put((3, 0, 0, 0))  # 停止命令

    def freshStatus(self, intervalTIme: int):
        for stepWork in self.diskStepWork.values():
            for cmp in stepWork.keys():
                cmp.refreshInterval = intervalTIme

    def getSelfStatus(self, device: str, index: int, state: str, stateCode: int, errorCode: int, deviceStatus: DeviceStatus):
        all_code = (stateCode << 8) | errorCode
        deviceStatus.error_code = all_code
        deviceStatus.status = state
        deviceStatus.run = True
        if errorCode != 0:
            deviceStatus.error_times = 1
            deviceStatus.finished = True
            deviceStatus.run = False
        return deviceStatus

    def onSetStatus(self, device: str, index: int, deviceStatus: DeviceStatus, ack_type=0):
        if self._handle_test_message:
            self._handle_test_message.onSetStatus(device, index, deviceStatus, ack_type)

    def onSetDeviceLog(self, device: str, item: int, toolID: int, logFile: str, ack_type=0):
        if self._handel_log_file:
            self._handel_log_file.onSetDeviceLog(device, item, toolID, logFile, ack_type)

    #  创建头部log内容
    def createTestLog(self, works, headerValue: list, device, index):
        logPath = os.path.join(self.configSetting.settings["LogPath"],
                                   f"{index}_{time.strftime('%Y%m%d_%H%M%S', time.localtime())}.txt")
        header = log_header_templete(headerValue)
        steps = "\nStep:               \n"
        testItemHeaders = ""
        stepIndex = 1
        for step in works:
            for tool in step:
                toolPath = os.path.join(self.configSetting.settings["Path"], tool.tool.tool_path)
                configPath = os.path.join(self.configSetting.settings["Path"], tool.tool.config_path)
                toolInfo = f"                       step{stepIndex}\n                              {toolPath}\n                              {configPath}\n"
                steps += toolInfo
                param = [tool.tool.tool_name, configPath, tool.startTime, tool.endTime,
                         str(tool.endTime - tool.startTime), tool.DeviceStatus.error_times, tool.DeviceStatus.status, tool.DeviceStatus.error_code]
                testItemHeader = log_result_templete(param)
                testItemHeaders += testItemHeader
            stepIndex += 1
        texts = header + steps + testItemHeaders
        with open(logPath, "w+") as f:
            f.write(texts)
            os.fsync(f.fileno())
        return logPath

    # 获取头部内容需要的参数
    def getHeaderArgs(self, workConfigMessage: WorkConfigMessage, startTime: str, endTime: str, lenght: int):
        # 获取SN
        index = workConfigMessage.disk_message.index
        strDevice = workConfigMessage.disk_message.device
        # diskMessage = DiskOnOff.DiskInfo(index, strDevice)
        SN = workConfigMessage.disk_message.serial_number
        Result = self.diskResult[index]
        Error_Code = 0
        # 获取MAC
        MAC = HandleIdentify.getMac()
        Disk = strDevice
        Index = index
        FWVersion = ""
        ModelName = ""
        Capacity = workConfigMessage.disk_message.all_capacity
        StartTime = startTime
        EndTime = endTime
        TotalCycle = lenght
        return [SN, Result, Error_Code, MAC, Disk, Index, FWVersion, ModelName, Capacity, StartTime, EndTime, TotalCycle]

    # 更新重启类信息
    def updateNotifyLostWorkConfig(self):
        # 将测试步骤存入离线单例类
        print("exec updateNotifyLostWorkConfig")
        path = "lostWorkConfig.pickle"
        lostTestStatus = LostWorkConfigMessage()
        lostTestStatus.first_connect = False
        print("path:",path)
        with open(path, 'wb') as fp:
            pickle.dump(lostTestStatus, fp)
            fp.flush()
            os.fsync(fp.fileno())

    def checkPortUse(self, port):
        try:
            import socket
            tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_server_socket.bind(('127.0.0.1', port))
            tcp_server_socket.close()
            print(f"{port} can use")
            return port
        except:

            use_port = port + 1
            print(f"port:{port} address already in use, need add one usr:{use_port}")
            return use_port

    #  判断测试结果状态
    def getResult(self, port):
        pass

    def endWork(self, device, index, status="", error_times=0, type_name="", status_id=""):
        print(f"send end work command:{type_name}")
        if self.diskWork.get(index):
            self.diskWork.pop(index)
        if self.diskResult.get(index):
            self.diskResult.pop(index)
        device_status = DeviceStatus()
        if status_id == 0:
            if hasattr(device_status, "status_id"):
                delattr(device_status, "status_id")
        else:
            device_status.status_id = status_id
        device_status.finished = True
        device_status.run = False
        device_status.error_times = error_times
        device_status.status = status
        self.onSetStatus(device, index, device_status)  # 发送结束状态

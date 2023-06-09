import platform
import random
import subprocess
import threading

import time
import command.handle.handleBase as handleBase
from command.event.EventPacketText import EventPacketText
import command.cmd.define as defines
from command.interfaces.netSend import NetSend
from common.lostWorkConfigMessage import LostWorkConfigMessage
from work.workManage import WorkManage
from command.cmd.text.diskPortMessage import DiskPortMessage


class HandleWork(handleBase.HandleBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)
        self.PORT = 0

    def handle_default(self, event) -> bool:
        if not isinstance(event, EventPacketText):
            return False
        # 开始任务
        if event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_START_TEST.value:
            data = event.packet_cmd.data
            work_manage = WorkManage()
            work_manageThread = threading.Thread(target=work_manage.startTest, args=(self, data))
            time.sleep(1)
            work_manageThread.start()
            return True
        # 停止任务
        elif event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_STOP_TEST.value:
            disk = DiskPortMessage.parse(event.packet_cmd.data)
            work_manage = WorkManage()
            time.sleep(0.5)
            work_manage.stopWork(disk)
            return True
        # 刷新界面 获取最新测试状态信息
        elif event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_FRESH_STATUS_TIME.value:
            intervalTIme = random.randint(event.packet_cmd.data["IntervalMin"],
                                          event.packet_cmd.data["IntervalMax"]) // 1000
            work_manage = WorkManage()
            time.sleep(0.5)
            work_manage.freshStatus(intervalTIme)
            return True
        # 重启客户端后 继续运行测试
        elif event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_CONTINUE_START_TEST.value:
            lostWorks = LostWorkConfigMessage()
            work_manage = WorkManage()
            for index, lostWorkConfig in lostWorks.lostWorkConfigMessageDict.items():
                workConfigMessage = lostWorks.workConfigMessageDict[index]
                works = lostWorkConfig
                startTime = lostWorks.startTimeDict[index]
                work_manageThread = threading.Thread(target=work_manage.continueTest, args=(workConfigMessage, works, startTime))
                time.sleep(0.5)
                work_manageThread.start()
            return True
        elif event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_SHUTDOWN.value:
            print("get shutdown CMD")
            currtPlatform = platform.system().lower()
            if currtPlatform == "windows":
                cmd = "shutdown -s -t 1"
                subprocess.run(cmd)
            elif currtPlatform == "linux":
                try:
                    cmd = "shutdown -h now"
                    subprocess.run(cmd)
                except:
                    time.sleep(10)
                    cmd = "poweroff"
                    subprocess.run(cmd)
            return True
        elif event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_REBOOT.value:
            print("get reboot CMD")
            currtPlatform = platform.system().lower()
            if currtPlatform == "windows":
                cmd = "shutdown -r -t 1"
                subprocess.run(cmd)
            elif currtPlatform == "linux":
                cmd = "reboot"
                subprocess.run(cmd)
            return True
        return False

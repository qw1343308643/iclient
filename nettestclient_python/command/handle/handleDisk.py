import json
import platform
import threading
import time
from time import sleep
import command.handle.handleBase as handleBase
from command.event.EventPacketText import EventPacketText
import command.cmd.define as defines
import config.config as config
import command.cmd.text.packetCmd as packetCmd
import command.cmd.text.diskMessage as diskMessage
import command.event.event as eventM
from command.interfaces.netSend import NetSend
from common.lostWorkConfigMessage import LostWorkConfigMessage
from common.systemCommon import get_etc_version_info


class HandleDisk(handleBase.HandleBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)
        self.start_enum_disk = False
        self.already_run = False

    def handle_default(self, event) -> bool:
        if not isinstance(event, EventPacketText):
            return False

        if event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_START_GET_DISK.value:
            self.addDisk()
            # 继续初始化
            e = eventM.Event("init")
            self.checkSystemVersion()
            time.sleep(3)
            lostWorks = LostWorkConfigMessage()
            if not lostWorks.first_connect:
                if not self.already_run:
                    event.packet_cmd.cmd = defines.NCMD_TYPE.NCMD_CONTINUE_START_TEST.value
                    self.already_run = True
                    return False
            return True
        elif event.packet_cmd.cmd == defines.NCMD_TYPE.NCMC_REFRESH_DISK.value:
            self.refreshDisk()
            return True
        return False

    def addDisk(self):
        time.sleep(1)
        currtPlatform = platform.system().lower()
        if currtPlatform == "windows":
            for index in range(0, 4):
                message = diskMessage.DiskMessage()
                message.index = index
                message.add = True
                message.device = f"{index}"
                message.all_capacity = 1024 * (index + 1)
                message.used_capacity = 1024 * (index + 1)
                message.disk_type = "RemoveableDisk"
                message.serial_number = f"{index}"
                cmd = packetCmd.PacketCmd()
                cmd.cmd = defines.NCMD_TYPE.NCMD_DISK.value
                self.sendCmdText(cmd, message.toJson())
        elif currtPlatform == "linux":
            self.guardDeviceOnPff()

    def refreshDisk(self):
        time.sleep(1)
        currtPlatform = platform.system().lower()
        if currtPlatform == "windows":
            for index in range(0, 4):
                message = diskMessage.DiskMessage()
                message.index = index
                message.add = True
                message.device = f"{index}"
                message.all_capacity = 1024 * (index + 1)
                message.used_capacity = 1024 * (index + 1)
                message.disk_type = "RemoveableDisk"
                message.serial_number = f"{index}"
                cmd = packetCmd.PacketCmd()
                cmd.cmd = defines.NCMD_TYPE.NCMD_DISK.value
                self.sendCmdText(cmd, message.toJson())
        elif currtPlatform == "linux":
            if self.diskChange != None:
                self.diskChange.FreshDisk()
                self.diskChange.FreshDisk(self.diskOnOff)
            else:
                self.guardDeviceOnPff()

    def guardDeviceOnPff(self):
        import expand.linuxDevice.example as devicelinux
        from expand.linuxDevice.linuxDevice import DiskOnOff
        self.diskChange = devicelinux.DiskChange()
        self.diskOnOff = DiskOnOff(self.sendCmdText)
        self.diskChange.AddNotify(self.diskOnOff)
        self.diskChange.Init()
        self.diskChange.FreshDisk()
        self.diskChange.FreshDisk(self.diskOnOff)


    def checkSystemVersion(self):
        data = get_etc_version_info()
        if data:
            cmd = packetCmd.PacketCmd()
            cmd.cmd = defines.NCMD_TYPE.NCMD_NODE_TEST_MESSAGE.value
            self.sendCmdText(cmd, json.dumps(data))

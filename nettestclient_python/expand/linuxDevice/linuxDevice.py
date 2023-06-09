import command.cmd.text.packetCmd as packetCmd
import command.cmd.text.diskMessage as diskMessage
import command.cmd.define as defines
import expand.linuxDevice.example as devicelinux
from work.workManage import WorkManage


class DiskOnOff(devicelinux.IDiskOnOffNotify):
    def __init__(self, sendCmdText):
        devicelinux.IDiskOnOffNotify.__init__(self)
        self.sendCmdText = sendCmdText

    @staticmethod
    def DiskInfo(nIndex, strDevice):
        print(f"DiskOn:{nIndex}:{strDevice}")
        diskInfo = devicelinux.DiskInfo()
        devicePath = strDevice
        sn = diskInfo.GetSN(devicePath)
        deviceType = diskInfo.GetDeviceType(devicePath)
        capacity = diskInfo.GetCapacity(devicePath)
        ullTotal = capacity.ullTotal
        free = capacity.ullFree
        message = diskMessage.DiskMessage()
        message.index = nIndex
        message.add = True
        message.device = f"{strDevice}"
        message.all_capacity = ullTotal
        message.used_capacity = free
        message.disk_type = deviceType
        message.serial_number = sn
        return message

    def DiskOn(self, nIndex, strDevice):
        workManage = WorkManage()
        current_nIndex = workManage.diskWork.get(nIndex)
        if current_nIndex:
            print(f"DiskOn:{nIndex}:{strDevice} return")
            return
        print(f"DiskOn:{nIndex}:{strDevice}")
        diskInfo = devicelinux.DiskInfo()
        devicePath = strDevice
        sn = diskInfo.GetSN(devicePath)
        deviceType = diskInfo.GetDeviceType(devicePath)
        capacity = diskInfo.GetCapacity(devicePath)
        ullTotal = capacity.ullTotal
        free = capacity.ullFree
        message = diskMessage.DiskMessage()
        message.index = nIndex
        message.add = True
        message.device = f"{strDevice}"
        message.all_capacity = ullTotal
        message.used_capacity = free
        message.disk_type = deviceType
        message.serial_number = sn
        cmd = packetCmd.PacketCmd()
        cmd.cmd = defines.NCMD_TYPE.NCMD_DISK.value
        self.sendCmdText(cmd, message.toJson())

    def DiskOff(self, nIndex, strDevice):
        workManage = WorkManage()
        current_nIndex = workManage.diskWork.get(nIndex)
        if current_nIndex:
            print(f"DiskOff:{nIndex}:{strDevice} return")
            return
        print(f"DiskOff:{nIndex}:{strDevice}")
        message = diskMessage.DiskMessage()
        message.index = nIndex
        message.add = False
        message.device = f"{strDevice}"
        cmd = packetCmd.PacketCmd()
        cmd.cmd = defines.NCMD_TYPE.NCMD_DISK.value
        self.sendCmdText(cmd, message.toJson())
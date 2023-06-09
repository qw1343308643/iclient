from command.cmd.text.testStatusMessage import TestStatusMessage
import command.cmd.define as defines

class DeviceStatus():
    def __init__(self) -> None:
        super().__init__()
        self.status_id = 0
        self.tool_id = 0
        self.current_cycles = 0
        self.error_times = 0
        self.error_code = 0
        self.current_pos = 0
        self.total_pos = 0
        self.run = False
        self.finished = False
        self.speed = ""
        self.status = ""
        self._extraInfo = []

    def addStatus(self, dataDict: dict):
        self._extraInfo.append(dataDict)

    def toTestStatus(self, device: str, index: int) -> TestStatusMessage:
        testStatus = TestStatusMessage()
        testStatus.disk_message.device = device
        testStatus.disk_message.index = index
        testStatus.run = self.run
        testStatus.finished = self.finished
        if hasattr(self, "status_id"):
            testStatus.status_id = self.status_id
        else:
            if hasattr(testStatus, "status_id"):
                delattr(testStatus, "status_id")
        testStatus.tool_id = self.tool_id
        testStatus.error_state = defines.ERROR_STATE.ERROR_STATE_ERROR.value if self.error_times > 0 else defines.ERROR_STATE.ERROR_STATE_OK.value
        # 磁盘容量更新

        testStatus.addStatus("CurrentCycles", f"{self.current_cycles}")
        testStatus.addStatus("ErrorTimes", f"{self.error_times}")
        if self.total_pos:
            testStatus.addStatus(
                "Progress", f"{(self.current_pos/(self.total_pos * 1.0))*100}%")
        if self.error_times > 0 and self.error_code > 0:
            testStatus.addStatus("ErrorCode", f"{self.error_code:04X}")
        if self.speed:
            testStatus.addStatus("Speed", f"{self.speed}")
        if self.status:
            testStatus.addStatus("Status", f"{self.status}")

        if self.error_times > 0 and "ErrorDescription" not in self._extraInfo:
            # 翻译ErrorCode
            pass
        if isinstance(self._extraInfo, dict):
            for key, value in self._extraInfo.items():
                testStatus.addStatus(key, value)
        return testStatus

    @staticmethod
    def parse(status):
        deviceStatus = DeviceStatus()
        deviceStatus.current_cycles = status.dwCurrentCycles
        deviceStatus.error_times = status.dwErrorTimes
        deviceStatus.error_code = status.dwErrorCode
        deviceStatus.current_pos = status.ullCurrentPos
        deviceStatus.total_pos = status.ullTotalPos
        deviceStatus.run = status.bRun
        deviceStatus.finished = status.bFinished
        deviceStatus.speed = status.strSpeed
        deviceStatus.status = status.strStatus
        deviceStatus._extraInfo = status.strExtraInfo
        return deviceStatus


if __name__ == '__main__':
    a = DeviceStatus()
    print(a.status_id)
    delattr(a, "status_id")
    delattr(a, "status_id")
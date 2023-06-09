

from command.cmd.text.dataMessage import DataMessage
from command.cmd.text.diskMessage import DiskMessage
from command.cmd.define import *
from config import config


class TestStatusMessage(DataMessage):
    def __init__(self) -> None:
        super().__init__()
        conf = config.Config()
        self.disk_message = DiskMessage()
        self.finished = False
        self.run = False
        if conf.settings.get("isSave"):
            self.save = conf.settings["isSave"]
        else:
            self.save = False
        self.status_id = ""
        self.tool_id = 0
        self.error_state = ERROR_STATE.ERROR_STATE_OK
        self._extraInfo = []

    def addStatus(self, key: str, value: str):
        self._extraInfo.append({"Key": key, "Value": value})

    def jsonDict(self) -> dict:
        info = super().jsonDict()
        info["DiskInfo"] = self.disk_message.jsonDict()
        info["Status"] = self._extraInfo
        info["Finished"] = self.finished
        info["Run"] = self.run
        info["ErrorState"] = self.error_state
        info["Save"] = self.save
        if hasattr(self, "status_id"):
            info["StatusID"] = self.status_id
        info["ToolID"] = self.tool_id
        return info

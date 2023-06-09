from __future__ import annotations
import json
import command.cmd.text.dataMessage as dataMessage


class DiskPortMessage(dataMessage.DataMessage):
    def __init__(self, message=None) -> None:
        super().__init__()
        self.device = ""
        self.index = 0
        if message and isinstance(message, DiskPortMessage):
            self.device = message.device
            self.index = message.index

    def jsonDict(self) -> dict:
        info = dict()
        info["Device"] = self.device
        info["Index"] = self.index
        return info

    @staticmethod
    def parse(content) -> DiskPortMessage:
        if isinstance(content, str):
            obj = json.loads(str)
        else:
            obj = content
        message = DiskPortMessage()
        message.device = obj["Device"]
        message.index = obj["Index"]
        return message

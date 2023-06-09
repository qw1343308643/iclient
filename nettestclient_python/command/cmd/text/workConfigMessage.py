import json
from command.cmd.text.dataMessage import DataMessage
from command.cmd.define import *
from command.cmd.text.diskMessage import DiskMessage


class ToolMessage(DataMessage):
    def __init__(self) -> None:
        super().__init__()
        self.status_id = ""
        self.tool_id = 0
        self.tool_path = ""
        self.tool_md5 = ""
        self.config_path = ""
        self.config_md5 = ""
        self.tool_name = ""
        self.main_tool = False

    def jsonDict(self) -> dict:
        info = super().jsonDict()
        info["StatusID"] = self.status_id
        info["ToolID"] = self.tool_id
        info["ToolPath"] = self.tool_path
        info["ToolMD5"] = self.tool_md5
        info["ConfigPath"] = self.config_path
        info["ConfigMD5"] = self.config_md5
        info["ToolName"] = self.tool_name
        info["MainTool"] = self.main_tool
        return info

    @staticmethod
    def parse(content) -> lambda: ToolMessage:
        step = ToolMessage()
        if isinstance(content, str):
            obj = json.loads(content)
        else:
            obj = content
        step.status_id = obj["StatusID"]
        step.tool_id = obj["ToolID"]
        step.tool_path = obj["ToolPath"]
        step.tool_md5 = obj["ToolMD5"]
        step.config_path = obj["ConfigPath"]
        step.config_md5 = obj["ConfigMD5"]
        step.tool_name = obj["ToolName"]
        step.main_tool = obj["MainTool"]
        return step


class StepMessage(DataMessage):
    def __init__(self) -> None:
        super().__init__()
        self.tools = []

    def jsonDict(self) -> dict:
        info = super().jsonDict()
        info["Tools"] = self.tools
        return info

    @staticmethod
    def parse(content) -> lambda: StepMessage:
        step = StepMessage()
        if isinstance(content, str):
            obj = json.loads(content)
        else:
            obj = content
        for item in obj["Tools"]:
            step.tools.append(ToolMessage.parse(item))
        return step

class WorkConfigMessage(DataMessage):
    def __init__(self) -> None:
        super().__init__()
        self.error_type = ERROR_TYPE.ERRORTYPE_STOP
        self.disk_message = DiskMessage()
        self.flow_name = ""
        self.status_id = ""
        self.step_configs = []

    def jsonDict(self) -> dict:
        info = super().jsonDict()
        info["ErrorType"] = self.error_type
        info["FlowName"] = self.flow_name
        info["Disk"] = self.disk_message
        info["StepConfigs"] = self.step_configs
        info["StatusID"] = self.status_id
        return info

    @staticmethod
    def parse(content, ignore=False) -> lambda: WorkConfigMessage:
        if isinstance(content, str):
            obj = json.loads(content)
        else:
            obj = content
        message = WorkConfigMessage()
        message.error_type = obj["ErrorType"]
        message.flow_name = obj["FlowName"]
        message.disk_message = DiskMessage.parse(obj["Disk"])
        message.EnvVariables = obj.get("EnvVariables")
        message.status_id = obj.get("StatusID")
        if ignore:
            return message
        for step in obj["StepConfigs"]:
            message.step_configs.append(StepMessage.parse(step))
        return message

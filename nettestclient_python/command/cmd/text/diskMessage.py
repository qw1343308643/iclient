from __future__ import annotations
import json
from command.cmd.text.diskCapacityMessage import DiskCapacityMessage


class DiskMessage(DiskCapacityMessage):
    def __init__(self, disk=None) -> None:
        super().__init__(disk)
        self.add = False
        self.disk_type = ""
        self.serial_number = ""
        if disk and isinstance(disk, DiskMessage):
            self.add = disk.used_capacity
            self.disk_type = disk.disk_type
            self.serial_number = disk.serial_number

    def jsonDict(self) -> dict:
        info = super().jsonDict()
        info["Add"] = self.add
        info["DiskType"] = self.disk_type
        info["SerialNumber"] = self.serial_number
        return info

    def toJson(self) -> str:
        info = self.jsonDict()
        return json.dumps(info)

    @staticmethod
    def parse(content) -> DiskMessage:
        capacity = DiskCapacityMessage.parse(content)
        disk = DiskMessage(capacity)
        if isinstance(content, str):
            obj = json.loads(content)
        else:
            obj = content

        disk.add = obj.get("Add", False)
        disk.disk_type = obj.get("DiskType", "")
        disk.serial_number = obj.get("SerialNumber", "")

        return disk

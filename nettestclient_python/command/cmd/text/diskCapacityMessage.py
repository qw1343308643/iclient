from __future__ import annotations
import json
from command.cmd.text.diskPortMessage import DiskPortMessage


class DiskCapacityMessage(DiskPortMessage):
    def __init__(self, capacity=None) -> None:
        super().__init__(capacity)
        self.used_capacity = 0
        self.all_capacity = 0
        if capacity and isinstance(capacity, DiskCapacityMessage):
            self.used_capacity = capacity.used_capacity
            self.all_capacity = capacity.all_capacity

    def jsonDict(self) -> dict:
        info = super().jsonDict()
        info["UsedCapacity"] = self.used_capacity
        info["AllCapacity"] = self.all_capacity
        return info

    @staticmethod
    def parse(content) -> DiskCapacityMessage:
        disk_port = DiskPortMessage.parse(content)
        disk = DiskCapacityMessage(disk_port)
        if isinstance(content, str):
            obj = json.loads(content)
        else:
            obj = content

        disk.used_capacity = obj.get("UsedCapacity", 0)
        disk.all_capacity = obj.get("AllCapacity", 0)

        return disk

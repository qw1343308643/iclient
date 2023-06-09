

class LostWorkConfigMessage:
    def __init__(self):
        if not hasattr(LostWorkConfigMessage, "_first_init"):
            LostWorkConfigMessage._first_init = True
            self.notify = True
            self.first_connect = True
            self.lostWorkConfigMessageDict = {}
            self.workConfigMessageDict = {}
            self.startTimeDict = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(LostWorkConfigMessage, "_instance"):
            LostWorkConfigMessage._instance = object.__new__(cls)
        return LostWorkConfigMessage._instance

    def set(self, lostWorkConfigMessage):
        self.first_connect = lostWorkConfigMessage.first_connect
        self.lostWorkConfigMessageDict = lostWorkConfigMessage.lostWorkConfigMessageDict
        self.workConfigMessageDict = lostWorkConfigMessage.workConfigMessageDict
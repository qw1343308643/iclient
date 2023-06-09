
class Factory:
    instanse = None

    def __new__(cls):
        if not cls.instanse:
            cls.instanse = super().__new__(cls)

        return cls.instanse

    def __init__(self) -> None:
        pass

    def GetProcesser():
        pass

import json


class DataMessage():

    def jsonDict(self) -> dict:
        info = dict()
        return info

    def toJson(self) -> str:
        info = self.jsonDict()
        return json.dumps(info)

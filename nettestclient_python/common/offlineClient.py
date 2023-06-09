import json
import os

from utility.fileLock import CFileLock


class OfflinClient:
    @staticmethod
    def addLostLogFiles(index: int, device: str, statusID: str, logFile: str):
        path = "lostTestLog.json"
        fileLock = CFileLock(path)
        if fileLock.acquire():
            try:
                index = str(index)
                if os.path.exists(path):
                    with open(path, "r") as f:
                        lostLogDict = json.load(f)
                    if isinstance(lostLogDict, dict):
                        if lostLogDict.get(index):
                            if isinstance(lostLogDict[index], list):
                                lostLogDict[index].append((logFile, index, device, statusID))
                            else:
                                logStatus = [(logFile, index, device, statusID)]
                                lostLogDict[index] = logStatus
                        else:
                            logStatus = [(logFile, index, device, statusID)]
                            lostLogDict[index] = logStatus
                    else:
                        lostLogDict = {}
                        lostLogDict[index] = [(logFile, index, device, statusID)]
                else:
                    lostLogDict = {}
                    lostLogDict[index] = [(logFile, index, device, statusID)]
                with open(path, "w") as f:
                    json.dump(lostLogDict, f)
                    f.flush()
                    os.fsync(f.fileno())
            finally:
                fileLock.release()


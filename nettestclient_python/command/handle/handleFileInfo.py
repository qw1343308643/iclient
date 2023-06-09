import threading
import command.handle.handleBase as handleBase
import command.cmd.define as defines
from command.handle.updateCompomenFile import UpdateCompomenFile
from command.interfaces.netSend import NetSend
from config import config

class HandleFileInfo():
    def __init__(self, updateObject: UpdateCompomenFile) -> None:
        super().__init__(next, updateObject)
        self.updateObject = updateObject

    def handle_default(self, event) -> bool:
        if event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_FILE_INFO.value:
            updateFile = self.updateObject
            c = config.Config()
            current_version = c.settings["Version"]
            server_version = event.packet_cmd.data
            if not server_version:
                print("no have update packet")
                updateFile.complete()
                return True
            ret = updateFile.compareVersion(current_version, server_version)
            if ret:
                updateApp = threading.Thread(target=updateFile.update)
                updateApp.start()
                return True
            else:
                updateFile.complete()
                return True
        return False

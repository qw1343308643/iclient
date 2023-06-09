import os.path
import subprocess
import sys
import threading

from command.cmd import define
from command.cmd.text import packetCmd
from command.handle import  commandBase
from command.handle.HandlePriority import HandlePriority
from command.handle.commandDownloadFile import CommandDownloadFile
import command.cmd.define as defines
from common.decompressingFile import DecompressingFile
from command.interfaces.netSend import NetSend
from config import config


class UpdateCompomenFile(commandBase.CommandBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)
        self.server_file_url = ""
        self.local_file_path = ""
        self.is_complete = False
        self.net_send = netSend
        self.update_event = None

    def handle_default(self, event) -> bool:
        if event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_FILE_INFO.value:
            HandlePriority.remove_instance(self)
            c = config.Config()
            current_version = c.settings["Version"]
            server_version = event.packet_cmd.data
            if not server_version:
                print("no have update packet")
                self.complete()
                return True
            ret = self.compareVersion(current_version, server_version)
            if ret:
                updateApp = threading.Thread(target=self.update)
                updateApp.start()
                return True
            else:
                self.complete()
                return True
        return False

    def check_version(self, path):
        self.server_file_url = path
        self.is_complete = False
        self.update_event = threading.Event()
        HandlePriority.add_instance(self)
        self.sendCompomenFileCmd(path)

    def complete(self):
        self.is_complete = True
        self.update_event.set()

    def update(self):
        command_download = CommandDownloadFile(None, self.net_send)
        ret = command_download.sendDownload(self.server_file_url, self.local_file_path)
        if ret:
            try:
                self.local_file_path = command_download.local_file_path
                total_path = os.path.dirname(os.path.abspath(sys.argv[0]))
                mimetype = DecompressingFile.get_compression_type(self.local_file_path)
                if mimetype:
                    DecompressingFile.unFile(self.local_file_path, total_path, mimetype)
                pid = os.getpid()
                cmd_args = ["kill", "-s", "9", str(pid)]
                print("update finish close client")
                subprocess.run(cmd_args, capture_output=True)
            except Exception as e:
                print("updateFile compression fail:", str(e))
            finally:
                self.update_event.set()

    def compareVersion(self, v1, v2):
        """
        compare version
        v1: first version number
        v2: second version number
        return:
            True if v1 < v2 else False
        """
        v1_part = [int(part) for part in v1.split(".")]
        v2_part = [int(part) for part in v2.split(".")]
        max_len = max(len(v1_part), len(v2_part))
        v1_part += [0] * (max_len - len(v1_part))
        v2_part += [0] * (max_len - len(v2_part))
        for i in range(max_len):
            if v1_part[i] < v2_part[i]:
                return True
        return False

    def sendCompomenFileCmd(self, compomenFile):
        cmd = packetCmd.PacketCmd()
        cmd.cmd = define.NCMD_TYPE.NCMD_FILE_INFO.value
        cmd.sub_cmd = define.NCMD_TYPE.NCMD_FILE_INFO_VERSION.value
        cmd.ack_type = define.ACK_TYPE.ACK_RESPONSE.value
        cmd.data = compomenFile
        response = cmd.toJson()
        print(response)
        self.net_send.sendMessage(response)

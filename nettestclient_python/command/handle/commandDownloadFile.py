import os
import struct
import threading
import command.cmd.define as defines

from command.cmd.binary.cmdFileMessage import CmdFileMessage
from command.event.eventPacketBinary import EventPacketBinary
from command.cmd.binary.packetCmd import PacketCmd as PacketCmdB
from command.handle import commandBase
from command.handle.HandlePriority import HandlePriority
from command.interfaces.netSend import NetSend
from config import config


class CommandDownloadFile(commandBase.CommandBase):
    def __init__(self, next, netSend: NetSend) -> None:
        super().__init__(next, netSend)
        self.net_send = netSend
        self.wait_time = 0
        self.is_complete = False
        self.local_file_path = ""
        self.server_url_path = ""
        self.download_event = threading.Event()


    def init_path(self, server_url_path, local_file_path):
        self.server_url_path = server_url_path
        self.local_file_path = local_file_path

    def handle_default(self, event):
        if not isinstance(event, EventPacketBinary):
            return False
        if event.packet_cmd.cmd == defines.NCMD_TYPE.NCMD_DOWNLOAD_FILE.value and event.packet_cmd.sub_cmd == defines.NCMD_TYPE.NCMD_FILE.value:
            self.wait_time = 0
            file_data = CmdFileMessage.parse(event.packet_cmd.data)
            if not self.local_file_path:
                server_download_file_name = file_data.file_name.replace("\0", "").replace("\\", os.sep)
                c = config.Config()
                download_dir = c.settings["Path"]
                self.local_file_path = os.path.join(download_dir, server_download_file_name.split(".")[0], os.path.basename(server_download_file_name))
            if self.writeFile(file_data, self.local_file_path):
                self.download_event.set()
                self.is_complete = True
            return True
        return False

    def sendDownLoadFileCmd(self):
        # 发送命令
        data = int.to_bytes(1, 4, "little", signed=False) + struct.pack(f"260s", self.server_url_path.encode("utf8"))
        targetData = PacketCmdB.getTargetData(data=data, cmd=defines.NCMD_TYPE.NCMD_DOWNLOAD_FILE.value, ack_type=defines.ACK_TYPE.ACK_RESPONSE.value)
        self.net_send.sendData(targetData)

    def wait(self, timeOut=None):
        while 1:
            ret = self.download_event.wait(60)
            if not ret:
                self.wait_time += 60
            else:
                break
            if self.wait_time >= 600:
                break
        return self.is_complete

    # def check_timeout(self):
    #     self.wait_time += 1
    #     print(f"download file:{self.server_url_path} {self.wait_time}s")
    #     if self.wait_time > 600 or not self.handle_isConnect():
    #         self.download_event.set()
    #         self.is_complete = False
    #         return
    #     elif self.download_event.is_set():
    #         return
    #     else:
    #         timer = threading.Timer(1, self.check_timeout)
    #         timer.start()

    def sendDownload(self, url, local_file_path):
        server_url_path = url
        local_file_path = local_file_path
        HandlePriority.add_instance(self)
        try:
            self.init_path(server_url_path, local_file_path)
            self.sendDownLoadFileCmd()
            ret = self.wait()
            return ret
        finally:
            HandlePriority.remove_instance(self)
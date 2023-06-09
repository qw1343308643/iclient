import os
from concurrent.futures.thread import ThreadPoolExecutor

from command.cmd.binary.cmdFileMessage import CmdFileMessage
from command.cmd.text.packetCmd import PacketCmd as PacketCmdText
from command.cmd.binary.packetCmd import PacketCmd as PacketCmdTBinary

class HandleSelfCmds():
    def __init__(self):
        if not hasattr(HandleSelfCmds, "_first_init"):
            HandleSelfCmds._first_init = True
            self.commandList = list()
            self.thread_pool = ThreadPoolExecutor(max_workers=1)

    def __new__(cls, *args, **kwargs):
        if not hasattr(HandleSelfCmds, "_instance"):
            HandleSelfCmds._instance = object.__new__(cls)
        return HandleSelfCmds._instance

    # 获取下载文件
    def handle_getDownLoadFile(self, fileMessage, initActive):
        fileNamePath = initActive.path
        log_dir = os.path.dirname(fileNamePath)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if not fileMessage.offset:
            with open(fileNamePath, "wb+") as f:
                f.write(bytes())
                f.flush()
                os.fsync(f.fileno())
        with open(fileNamePath, "ab+") as f:
            f.seek(fileMessage.offset)
            f.write(fileMessage.buf)
            f.flush()
            os.fsync(f.fileno())
        if fileMessage.is_complete:
            self.commandList.remove(initActive)

    def parse(self, message):
        if isinstance(message, str):
            cmd = PacketCmdText.parse(message)
        else:
            cmd = PacketCmdTBinary.parse(message)
        for initActive in self.commandList:
            if (cmd.cmd, cmd.sub_cmd, cmd.packet_type, cmd.ack_type) == initActive.except_response:
                if hasattr(self, initActive.handler):
                    fileMessage = CmdFileMessage.parse(cmd.data)
                    path = fileMessage.file_name.replace("\0", "").replace("\\", os.sep)
                    if path == initActive.serverPath:
                        methond = getattr(self, initActive.handler)
                        self.thread_pool.submit(methond, fileMessage, initActive)
                        return True
        return False




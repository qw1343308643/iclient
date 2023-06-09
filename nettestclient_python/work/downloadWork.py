import os
from command.cmd.text.workConfigMessage import WorkConfigMessage
from command.handle.commandDownloadFile import CommandDownloadFile
from command.handle.handleSelfCmds import HandleSelfCmds
from common.decompressingFile import DecompressingFile
from common.deviceStatus import DeviceStatus
from config.config import Config
from config.errorCode import ERROR_CODE_ERROR,NetTestClientError


class DownLoadWork:
    def __init__(self,workConfig: WorkConfigMessage, tool, netSend, onSetStatus):
        self.workConfig = workConfig
        self.device = self.workConfig.disk_message.device
        self.index = self.workConfig.disk_message.index
        self.tool = tool  # [StepMessage]
        self.netSend = netSend
        self.onSetStatus = onSetStatus
        self.handle_selfCmds = HandleSelfCmds()

        # 导出本地工具路径
        jsonConfig = Config()
        self.dirPath = jsonConfig.settings["Path"]  # 下载的目录
        self.descPath = jsonConfig.settings["DescPath"]  # 解压的目录

    # 判断文件是否存在 不存在则发送下载命令
    def download(self):
        file_md5_dict = {}
        compare_file_md5_dict = {}
        descDict = {}  # 存储压缩文件
        need_download_file_list = []
        file_md5_dict[self.tool.tool_path.replace("\\", os.sep)] = self.tool.tool_md5
        file_md5_dict[self.tool.config_path.replace("\\", os.sep)] = self.tool.config_md5
        print("tool.tool_path:",self.tool.tool_path)
        for server_file_url, md5 in file_md5_dict.items():
            file_name = os.path.basename(server_file_url).split(".")[0]
            print("file_name",file_name)
            file_path = os.path.join(file_name, md5, os.path.basename(server_file_url))
            local_file_path = os.path.join(self.dirPath, file_path)
            print("local_file_path:",local_file_path)
            if os.path.exists(local_file_path):
                # 文件已存在,计算MD5是否一致
                print("file already exit, check md5 value:",local_file_path)
                fileMD5 = self.netSend.getFileMD5(local_file_path)
                if fileMD5 != md5:
                    need_download_file_list.append((server_file_url, local_file_path, md5))
                else:
                    descFile = os.path.join(self.descPath, os.path.join(file_name, md5), str(self.index))
                    if not os.path.exists(descFile):
                        if DecompressingFile.get_compression_type(local_file_path):
                            descDict[local_file_path] = md5
            else:
                need_download_file_list.append((server_file_url, local_file_path, md5))
            compare_file_md5_dict[local_file_path] = md5

        for server_file_url, local_file_path, md5 in need_download_file_list:
            print("file no exit, start download")
            command_download = CommandDownloadFile(None, self.netSend.net_send)
            ret = command_download.sendDownload(server_file_url, local_file_path)
            if ret:
                if DecompressingFile.get_compression_type(local_file_path):
                    descDict[local_file_path] = md5
            else:
                return self.download_error("download file out time")
        print(compare_file_md5_dict)
        print("descDict:", descDict)
        for file, md5 in compare_file_md5_dict.items():
            fileMD5 = self.netSend.getFileMD5(file)
            if fileMD5 != md5:
                return self.download_error("MD5 compare fail")
        # 解压文件
        try:
            for source_path, md5 in descDict.items():
                file_name = os.path.basename(source_path).split(".")[0]
                total_apth = os.path.join(self.descPath, os.path.join(file_name, md5), str(self.index))
                compression_type = DecompressingFile.get_compression_type(source_path)
                if compression_type:
                    DecompressingFile.unFile(source_path, total_apth, compression_type)
        except NetTestClientError as e:
            return self.download_error(str(e))
        except Exception as e:
            print(f"unzip fail")
            return self.download_error(str(e))
        return {"flag": True, "status": "就绪"}

    def download_error(self, error_status):
        print("error_status:", error_status)
        status = DeviceStatus()
        status.finished = True
        status.run = False
        status.error_times += 1
        status.error_code = ERROR_CODE_ERROR.TIME_OUT.value
        status.status = error_status
        self.onSetStatus(self.device, self.index, status)
        return {"flag": False, "status": status.status}
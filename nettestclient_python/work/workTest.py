import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime

from common.deviceStatus import DeviceStatus
from config import config
from config.config import Config
from config.errorCode import NetTestClientError, ERROR_CODE_ERROR


class Work:
    def __init__(self, workConfig=None, tool=None):
        # 任务运行状态
        self.WorkConfig = workConfig
        self.run = True
        self.error_flag = False
        self.isReboot = False
        # # 测试信息
        self.tool = tool
        self.config = config.Config()
        self.DeviceStatus = DeviceStatus()
        jsonConfig = Config()
        #time
        self.startTime = datetime.now()
        self.endTime = datetime.now()
        self.dirPath = jsonConfig.settings["Path"]  # 下载的目录
        self.descPath = jsonConfig.settings["DescPath"]  # 解压的目录
        if not os.path.exists(self.dirPath):
            os.mkdir(self.dirPath)

        if not os.path.exists(self.descPath):
            os.mkdir(self.descPath)
        self.workParam = dict()
        self.parseTool()
        self.commentUpdate()

    def parseTool(self):
        tool_name = os.path.basename(self.tool.tool_path.replace("\\", os.sep)).split(".")[0]
        tool_path = os.path.join(self.descPath, tool_name, self.tool.tool_md5, str(self.WorkConfig.disk_message.index))
        print("tool_path:", tool_path)
        self.workParam["Tool"] = self.get_tool_path(tool_path)
        if self.workParam["Tool"] == None:
            raise NetTestClientError("not found tool path")
        self.workParam["MD5"] = self.tool.tool_md5

        if ".zip" in self.tool.config_path or ".7z" in self.tool.config_path or ".tar" in self.tool.config_path:
            print("config is tar")
            config_name = os.path.basename(self.tool.config_path.replace("\\", os.sep)).replace(".7z", "").replace(
                        ".zip", "").replace(".tar.gz", "").replace(".tar", "").split(".")[0]
            config_path = os.path.join(self.descPath, config_name, self.tool.config_md5,  str(self.WorkConfig.disk_message.index))
            print("config_path:", config_path)
            files = [os.path.abspath(os.path.join(r, f)) for r, _, fs in os.walk(config_path) for f in fs]
            # files = [os.path.join(root, filename) for root, dirs, files in os.walk(config_path) for filename in files]
            print("files:", files)
            sysFilePath = "\n".join(files)
            print("sysFilePath:", sysFilePath)
        else:
            config_name = os.path.basename(self.tool.config_path.replace("\\", os.sep)).split(".")[0]
            file_path = os.path.join(config_name, self.tool.config_md5, os.path.basename(self.tool.config_path.replace("\\", os.sep)))
            sysFilePath = os.path.join(self.dirPath, file_path)
        self.workParam["Config"] = sysFilePath.replace("\\", os.sep)
        self.workParam["Device"] = self.WorkConfig.disk_message.device
        self.workParam["Index"] = self.WorkConfig.disk_message.index
        path = self.config.settings["LogPath"]
        if path[-1] != os.sep:
            path = path + os.sep
        self.workParam["LogDir"] = path
        self.workParam["StatusID"] = self.tool.status_id
        self.workParam["ToolID"] = self.tool.tool_id
        self.workParam["ToolName"] = self.tool.tool_name
        self.workParam["MainTool"] = self.tool.main_tool
        print(self.workParam)

    def get_tool_path(self, path):
        if platform.system().lower() == "windows":
            pycute_path = self.get_file_path("main.py", path, False)  # 精确查找main.py文件
            if pycute_path:
                return pycute_path

            execute_path = self.get_file_path(".exe", path, )  # 模糊查找所有可执行文件
            if execute_path:
                return execute_path

            raise NetTestClientError(ERROR_CODE_ERROR.CANNOT_FOUND_SPECIFY_FILE.value)
        elif platform.system().lower() == "linux":
            pycute_path = self.get_file_path(".json", path, True, True)  # 精确查找.json文件
            if pycute_path:
                return pycute_path

            pycute_path = self.get_file_path("main.py", path, True, True)  # 精确查找main.py文件
            if pycute_path and "cmpLib" not in pycute_path:
                return pycute_path

            execute_path = self.get_file_path("", path, False, True)  # 模糊查找所有可执行文件
            print("execute_path:",execute_path)
            if execute_path:
                return execute_path
        else:
            pass

    def get_file_path(self, fileName, dirName, fuzzy=True, isLinux=False):
        returnList = []

        def search_file_in_dir(fileName, dirName, fuzzy, isLinux):
            if not os.path.isdir(dirName):
                sys.exit('directory does not exist.(%s)' % (dirName))
            fileList = [x for x in os.listdir(dirName) if os.path.isfile(os.path.join(dirName, x))]
            dirList = [i for i in os.listdir(dirName) if os.path.isdir(os.path.join(dirName, i))]
            if fuzzy:
                for name in fileList:
                    if fileName in name:
                        returnList.append(os.path.join(dirName, name))
            else:
                if isLinux:
                    # for name in fileList:
                    #     path = os.path.join(dirName, name)
                    #     if ".json" in path:
                    #         with open(path, "r") as f:
                    #             info = json.loads(f.read())
                    #             entry = info.get("Entry")
                    #             if entry:
                    #                 dirname = os.path.dirname(path)
                    #                 exe_path = os.path.join(dirname, entry)
                    #                 return exe_path
                    for name in fileList:
                        path = os.path.join(dirName, name)
                        if "." not in path:
                            p = "'{print $1}'"
                            cmd = f'ls -l "{path}" | awk {p}'
                            ret = subprocess.run(cmd, shell=True, capture_output=True)
                            out = ret.stdout.decode()
                            xcount = 0
                            for i in out:
                                if "x" in i:
                                    xcount += 1
                                    if xcount == 3:
                                        returnList.append(path)
                    if len(returnList) == 0:
                        for name in fileList:
                            path = os.path.join(dirName, name)
                            if ".so" not in path and ".txt" not in path and "cmpLib" not in path and ".json" not in path and ".bat" not in path\
                                    and ".xml" not in path and ".ini" not in path:
                                p = "'{print $1}'"
                                cmd = f'ls -l "{path}" | awk {p}'
                                ret = subprocess.run(cmd, shell=True, capture_output=True)
                                out = ret.stdout.decode()
                                xcount = 0
                                for i in out:
                                    if "x" in i:
                                        xcount += 1
                                        if xcount == 3:
                                            returnList.append(path)
                else:
                    if fileName in fileList:
                        returnList.append(os.path.join(dirName, fileName))
            dirListLen = len(dirList)
            if dirListLen > 0:
                for d in dirList:
                    search_file_in_dir(fileName, os.path.join(dirName, d), fuzzy, isLinux)
            return returnList

        search_file_in_dir(fileName, dirName, fuzzy, isLinux)
        if len(returnList) >= 1:
            if fileName == ".json":
                for path in returnList:
                    if ".json" in path:
                        with open(path, "r") as f:
                            info = json.loads(f.read())
                            entry = info.get("Entry")
                            if entry:
                                dirname = os.path.dirname(path)
                                exe_path = os.path.join(dirname, entry)
                                return exe_path
                return None
            return returnList[0]
        else:
            return None

    def commentUpdate(self):
        dirPath, _ = os.path.split(os.path.abspath(sys.argv[0]))
        libDeviceFilePath_0 = os.path.join(dirPath, "libCMPLoader.so")
        libDeviceFilePath_1 = os.path.join(dirPath, "libCMPLoader.so.1")
        libDeviceFilePath_1__5 = os.path.join(dirPath, "libCMPLoader.so.1.9")
        toolDirPath = os.path.dirname(self.workParam["Tool"])
        cpCmd_0 = f'cp -d "{libDeviceFilePath_0}" "{toolDirPath}"'
        cpCmd_1 = f'cp -d "{libDeviceFilePath_1}" "{toolDirPath}"'
        cpCmd_1__5 = f'cp -d "{libDeviceFilePath_1__5}" "{toolDirPath}"'
        subprocess.run(cpCmd_1__5, shell=True, capture_output=True)
        subprocess.run(cpCmd_1, shell=True, capture_output=True)
        subprocess.run(cpCmd_0, shell=True, capture_output=True)
        cmp_path = os.path.join(toolDirPath, "cmpLib")
        if not os.path.exists(cmp_path):
            dirpath = os.path.join(os.path.split(os.path.abspath(sys.argv[0]))[0], "cmpLib")
            print("dirpath:",dirpath)
            shutil.copytree(dirpath, cmp_path)


def get_file_path(fileName, dirName, fuzzy=True, isLinux=False):
    returnList = []

    def search_file_in_dir(fileName, dirName, fuzzy, isLinux):
        if not os.path.isdir(dirName):
            sys.exit('directory does not exist.(%s)' % (dirName))
        fileList = [x for x in os.listdir(dirName) if os.path.isfile(os.path.join(dirName, x))]
        dirList = [i for i in os.listdir(dirName) if os.path.isdir(os.path.join(dirName, i))]
        if fuzzy:
            for name in fileList:
                if fileName in name:
                    returnList.append(os.path.join(dirName, name))
        else:
            if isLinux:
                # for name in fileList:
                #     path = os.path.join(dirName, name)
                #     if ".json" in path:
                #         with open(path, "r") as f:
                #             info = json.loads(f.read())
                #             entry = info.get("Entry")
                #             if entry:
                #                 dirname = os.path.dirname(path)
                #                 exe_path = os.path.join(dirname, entry)
                #                 return exe_path
                for name in fileList:
                    path = os.path.join(dirName, name)
                    if "." not in path:
                        p = "'{print $1}'"
                        cmd = f'ls -l "{path}" | awk {p}'
                        ret = subprocess.run(cmd, shell=True, capture_output=True)
                        out = ret.stdout.decode()
                        xcount = 0
                        for i in out:
                            if "x" in i:
                                xcount += 1
                                if xcount == 3:
                                    returnList.append(path)
                if len(returnList) == 0:
                    for name in fileList:
                        path = os.path.join(dirName, name)
                        if ".so" not in path and ".txt" not in path and "cmpLib" not in path and ".json" not in path and ".bat" not in path \
                                and ".xml" not in path:
                            p = "'{print $1}'"
                            cmd = f'ls -l "{path}" | awk {p}'
                            ret = subprocess.run(cmd, shell=True, capture_output=True)
                            out = ret.stdout.decode()
                            xcount = 0
                            for i in out:
                                if "x" in i:
                                    xcount += 1
                                    if xcount == 3:
                                        returnList.append(path)
            else:
                if fileName in fileList:
                    returnList.append(os.path.join(dirName, fileName))
        dirListLen = len(dirList)
        if dirListLen > 0:
            for d in dirList:
                search_file_in_dir(fileName, os.path.join(dirName, d), fuzzy, isLinux)
        return returnList

    search_file_in_dir(fileName, dirName, fuzzy, isLinux)
    if len(returnList) >= 1:
        if fileName == ".json":
            for path in returnList:
                if ".json" in path:
                    with open(path, "r") as f:
                        info = json.loads(f.read())
                        entry = info.get("Entry")
                        if entry:
                            dirname = os.path.dirname(path)
                            exe_path = os.path.join(dirname, entry)
                            return exe_path
            return None
        return returnList[0]
    else:
        return None

# if __name__ == '__main__':
#     path = "/home/lyf/SmartV1.5.2_arm_debug/311231231231323"
#     pycute_path = get_file_path(".json", path, True, True)  # 精确查找.json文件
#     if pycute_path:
#         print("pycute_path:",pycute_path)
#
#     pycute_path = get_file_path("main.py", path, True, True)  # 精确查找main.py文件
#     if pycute_path and "cmpLib" not in pycute_path:
#         print("pycute_path1:",pycute_path)
#
#     execute_path = get_file_path("", path, False, True)  # 模糊查找所有可执行文件
#     print("execute_path:", execute_path)
#     if execute_path:
#         print("execute_path:",execute_path)


import datetime
import mimetypes
import os
import platform
import re
import subprocess
import sys


def get_home_dir():
    '''
    获得home目录
    :return:
    '''
    if sys.platform == 'win32':
        homedir = os.environ['USERPROFILE']
        homedir = os.path.join(homedir, r"AppData\Local\cmpLib")
    elif sys.platform == 'linux' or sys.platform == 'darwin':
        homedir = os.path.expanduser("~")
        homedir = os.path.join(homedir, r"cmpLib")
    else:
        raise NotImplemented(f'Error! Not this system. {sys.platform}')
    return homedir

def get_host_type():
    currtPlatform = platform.system().lower()
    if currtPlatform == "windows":
        host_type = "windows"
    elif currtPlatform == "linux":
        cmd = "uname -a"
        ret = subprocess.run(cmd, shell=True, capture_output=True)
        message = ret.stdout.decode().lower()
        if "aarch64" in message:
            host_type = "Arm64"
        elif "ubuntu" in message:
            host_type = "Ubuntu"
        else:
            host_type = "Linux"
        mtk_text = read_etc_version()
        if mtk_text:
            if "MTK" in mtk_text or "mtk" in mtk_text:
                host_type = "MTK"
    else:
        host_type = ""
    return host_type

def is_windows_or_linux():
    currtPlatform = platform.system().lower()
    if currtPlatform == "windows":
        return currtPlatform
    elif currtPlatform == "linux":
        return currtPlatform
    else:
        return ""

def get_platform():
    currtPlatform = platform.system().lower()
    if currtPlatform == "windows":
        return currtPlatform
    elif currtPlatform == "linux":
        cmd = "file /usr/bin/ls"
        ret = subprocess.run(cmd, shell=True, capture_output=True)
        message = ret.stdout.decode().lower()
        if "arm" in message:
            return "arm"
        mtk_text = read_etc_version()
        if mtk_text:
            message = ret.stdout.decode().lower()
            if "MTK" in message or "mtk" in message:
                return "mtk"
        return "linux"

def is_valid_datetime(data_str, date_format="%Y-%m-%d %H:%M:%S"):
    try:
        datetime.datetime.strptime(data_str, date_format)
        return True
    except:
        return False

# def get_compression_type(path):
#     archive_headers = [
#         (b"\x42\x5a\x68", "bzip2"),
#         (b"\x50\x4b\x03\x04", "zip"),
#         (b"\x50\x4d\x4f\x43\x43\x41\x54", "7z"),
#         (b"\x75\x73\x74\x61\x72", "tar"),
#         (b"\x1f\x8b\x08\x00\x00\x00\x00", "tar.gz"),
#         (b"\x1f\x8b\x08", "gzip")
#     ]
#     with open(path, "rb") as f:
#         file_headers = f.read(max(len(header) for header, _ in archive_headers))
#         for header, archive_type in archive_headers:
#             if file_headers.startswith(header):
#                 is_archive = True
#                 break
#         else:
#             is_archive = False
#     return is_archive, archive_type
def read_etc_version():
    path = "/etc/version"
    if os.path.exists(path):
        with open(path, "rb") as f:
            text = str(f.read())
            return text
    else:
        return None

def readline_etc_version():
    path = "/etc/version"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="gbk") as f:
                text = f.readlines()
                return text
        except:
            try:
                with open(path, "r", encoding="utf8") as f:
                    text = f.readlines()
                    return text
            except:
                return None
    else:
        return None


def get_etc_version_info():
    texts = readline_etc_version()
    if texts:
        data = {
            "EnvVariables": [
            ]
        }
        for text in texts:
            text = str(text)
            if ":" in text:
                info = text.split(":")
                if len(info) == 2:
                    key_text = info[0].replace("\\r", "").replace("\\n", "").replace("\r", "").replace("\n", "")
                    value_text = info[1].replace("\\r", "").replace("\\n", "").replace("\r", "").replace("\n", "")
                    data["EnvVariables"].append({"Key": key_text, "Value": value_text})
        print("EnvVariables:", data)
        return data
    else:
        return None






# import argparse
# import json
# import os
# import platform
# import socket
# import subprocess
# import sys
# import threading
# import time
# import uuid
#
# from command.handle.handleIdentity import HandleIdentify
# from config.config import Config
# from main import WebsocketMain
#
#
# def getHostType():
#     HostType = platform.system().lower()
#     if HostType == "linux":
#         cmd = "uname -a"
#         ret = subprocess.run(cmd, shell=True, capture_output=True)
#         message = ret.stdout.decode().lower()
#         if "aarch64" in message:
#             HostType = "Arm64"
#         elif "ubuntu" in message:
#             HostType = "Ubuntu"
#         else:
#             HostType = "Linux"
#         path = "/etc/version"
#         if os.path.exists(path):
#             _fd = os.open(path, os.O_RDWR, mode=0o600)
#             size = 512
#             info_str = os.read(_fd, size)
#             try:
#                 message = info_str.decode()
#                 if "MTK" in message or "mtk" in message:
#                     HostType = "MTK"
#             except:
#                 print("mtk file decode continue")
#     return HostType
#
#
#
# if __name__ == '__main__':
#     path = "virtualMainNodes.txt"
#     threadingAppList = []
#
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-ip", help="severs ip")
#     pr = parser.parse_args()
#     ip = pr.ip
#     try:
#         if ip:
#             cfg = "config/appsettings.json"
#             with open(cfg, "r") as f:
#                 info = json.loads(f.read())
#             with open(cfg, "w") as f:
#                 info["WebSocketUrl"] = f"ws://{ip}/api/Server/connect"
#                 json.dump(info, f, indent=4)
#     except Exception as e:
#         print("ip cfg error:", e)
#         sys.exit()
#
#
#     if not os.path.exists(path):
#         for i in range(5):  # 开n个虚拟节点
#             guid = uuid.uuid4()
#             info = {
#                 "HostName": socket.gethostname(),
#                 "Version": "1.0",
#                 "FirstConnect": 1,
#                 "HostType": getHostType(),
#                 "MacAddr": HandleIdentify.getMac()
#             }
#             info["HostName"] = f"{info['HostName']}_{guid}"
#             info["VirtualMacAddr"] = f"{guid}"
#             info["VirtualIPAddress"] = f"{guid}"
#             info = json.dumps(info)
#             with open(path, "a+") as f:
#                 f.write(info)
#                 f.write("\n")
#
#         with open(path, 'r') as f:
#             hosts = f.readlines()
#         for host in hosts:
#             host = json.loads(host)
#             config = Config(virtualNode=host)
#             config.load()
#             webTask = WebsocketMain(config)
#             threadingApp = threading.Thread(target=webTask.start, name=host["HostName"])
#             threadingApp.start()
#             time.sleep(0.5)
#     else:
#         with open(path, 'r') as f:
#             hosts = f.readlines()
#         for host in hosts:
#             host = json.loads(host)
#             config = Config(virtualNode=host)
#             config.load()
#             webTask = WebsocketMain(config)
#             threadingApp = threading.Thread(target=webTask.start, name=host["HostName"])
#             threadingApp.start()
#             time.sleep(0.5)
#             threadingAppList.append(threadingApp)
#
#     while 1:
#         # for threadingApp in threadingAppList:
#         #     print(f"name:{threadingApp.name},status:{threadingApp.is_alive()}")
#         time.sleep(10)
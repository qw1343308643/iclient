import mycmp
import os
import threading
import sys


def getContextInfo():
    print("getContextInfo")
    clientContext = client.CMPGetClientContext()
    print("获取当前项目名称:",clientContext.GetFlowName())
    currnetStepIndex = clientContext.GetCurrentStepIndex()
    currnetToolIndex = clientContext.GetCurrentToolIndex()
    print("获取当前工具名称:",clientContext.GetToolName(currnetStepIndex, currnetToolIndex))

currentDir = os.getcwd()
client = mycmp.MyCMPClinet()
bRet = client.InitCMP(sys.argv[0])
if not bRet:
    print("InitCMP fail")
else:
    timer = threading.Timer(30, getContextInfo)
    timer.start()
    print("进入等待状态...")
    client.WaitForDone()
    print("finished")
    print("log:",client.CMPGetLogs(0))

# str = input("就绪")
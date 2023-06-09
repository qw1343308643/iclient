from enum import Enum

NCMD_FLAG = 0x1620622b

SUB_CMD_DOWNLOAD_FILE_COMPLETE = 1
NCMD_GET_OFFLINE_INFO_COMPLETE = 1


class PACKET_TYPE(Enum):
    PACKET_NORMAL = 0
    PACKET_ACK = 1
    PACKET_RESPONSE = 2


class ACK_TYPE(Enum):
    ACK_NONE = 0
    ACK_ACK = 1
    ACK_RESPONSE = 2
    ACK_ALL = 3


class ERROR_STATE(Enum):
    ERROR_STATE_OK = 0
    ERROR_STATE_ERROR = 1
    ERROR_STATE_WARNING = 2


class ERROR_TYPE(Enum):
    ERRORTYPE_CONTINUE = 0
    ERRORTYPE_STOP = 1


class NCMD_TYPE(Enum):
    NCMD_FILE_INFO_VERSION = 1  # 获取指定文件的版本号
    NCMD_INDETITY = 11  # 获取客户端信息
    NCMD_LOG_FILE = 44  # 发送的是一个日志文件
    NCMD_DISK = 15  # 本次发送的是磁盘信息
    NCMD_START_GET_DISK = 16  # 客户端离线后,服务器发送此命令,表示初始化完成，可正常发送后续上下盘信息. (初始化未完成前不可发送任何命令)
    NCMD_START_TEST = 18  # 开始测试
    NCMD_STOP_TEST = 20  # 停止测试
    NCMD_TEST_MESSAGE = 22  # 测试状态
    NCMD_LOG = 24  #
    NCMD_DOWNLOAD_FILE = 25  # 下载文件
    NCMD_GET_OFFLINE_INFO = 26  # 离线文件,状态
    NCMD_FILE = 31  #
    NCMD_SHUTDOWN = 33  # 关键
    NCMD_REBOOT = 34  # 重启
    NCMC_REFRESH_DISK = 35  # 重新枚举磁盘
    NCMD_SET_SYSTEM_TIME = 36  # 设置系统时间
    NCMD_FILE_INFO = 37  # 文件信息
    NCMD_DISK_SERIAL = 38  # 序列号
    NCMD_FRESH_STATUS_TIME = 39  # 刷新
    NCMD_POWERSUSPEND = 40  #
    NCMD_CONTINUE_START_TEST = 41  # 重启后继续测试
    NCMD_NODE_TEST_MESSAGE = 42  #

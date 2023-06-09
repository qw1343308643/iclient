import enum

from utility.singleton import Singleton


class NetTestClientError(Exception):
    def __init__(self, err):
        self.err = err

    def __str__(self):
        if self.err:
            return self.err


class ERROR_CODE_STATUS(enum.Enum):
    STATUS_CLIENT = 1,
    SEND_LOG = 2
    FIND_LOADER_FILE = 3
    H2TEST = 4
    BURNIN_TEST = 5
    FORMAT = 6
    LOAD_LOADER = 7
    COPY_FILE = 8
    COMPARE_FILE = 9
    FILE_HYPER = 10
    SECTOR_HYPER = 11
    SPEED_TEST = 12
    READ_ECC = 13
    POWER_CONSUMER = 14
    FILL_DISK = 15
    GET_SMART = 16
    WRITE_LOG = 17
    DELETE_FILE = 18
    STATE_INIT = 19
    STATE_WAIT = 20
    STATUS_SERVER = 64


class ERROR_CODE_ERROR(enum.Enum):
    NO_CARD = 1
    TIME_OUT = 2
    INVALID_DEVICE = 3
    CONTROL_NOT_EQUAL = 4
    NO_ENOUGH_AUTH_NUMBER = 5
    GET_DISK_SPACE_FAIL = 6
    OPEN_FILE_FAIL = 7
    FILE_SIZE_NOT_EQUAL = 8
    CREATE_FILE_MAP_FAIL = 9
    CREATE_FILE_MAP_VIEW_FAIL = 10
    READ_FILE_FAIL = 11
    WRITE_FILE_FAIL = 12
    SET_FILE_SIZE_FAIL = 13
    POWER_ON_FAIL = 14
    POWER_OFF_FAIL = 15
    POWER_ON_TIMEOUT = 16
    POWER_OFF_TIMEOUT = 17
    FORMAT_FAIL = 18
    NO_FILES_ON_DISK = 19
    NO_FILES_IN_SRC_DIR = 20
    MORE_ENOUGH_SPACE = 21
    DELETE_FILE_FAIL = 22
    REMOVE_DIR_FAIL = 23
    OPEN_DISK_FAIL = 24
    WRITE_SECTORS_FAIL = 25
    READ_SECTORS_FAIL = 26
    DATA_MISMATCH = 27
    SET_FILE_POINTER_FAIL = 28
    SPEED_LOWER = 29
    LOCK_VOLUME_FAIL = 30
    CMD_AUTH_FAIL = 31
    CHECK_BLOCK_FAIL = 32
    ECC_HIGHER = 33
    CURRENT_HIGHER = 34
    GET_FILE_SIZE_FAIL = 35
    CREATE_DIR_FAIL = 36
    H2TEST_ERROR = 37
    WINDOW_SHUT_DOWN_ILLEGALLY = 38
    CANNOT_FOUND_SPECIFIED_PATH = 39
    CREATE_PROCESS_FAIL = 40
    SET_H2TEST_FAIL = 41
    CANNOT_FOUND_SPECIFIED_WINDOW = 42
    VIRTUAL_ALLOC_FAIL = 43
    SAMRT_HIGHER = 44
    GET_SAMRT_FAIL = 45
    BURN_FAIL = 46
    GET_DISK_NUMBER_FAIL = 47
    OPEN_LOG_FAIL = 48
    WRITE_LOG_FAIL = 49
    GET_MAX_TEMPERATURE_FAIL = 50
    MAX_TEMPERATURE_HIGHER = 51
    CURRENT_TEMPERATUER_HIGHER = 52
    ILLEGAL_POWER_OFF = 53
    TRANSFER_MODE_NOT_EQUAL_IN_ONE = 54
    TRANSFER_MODE_NOT_EQUAL = 55
    MAX_ROLLBACK_HIGHER = 56
    DOWNLOAD_FILE_FAIL = 57
    DOWNLOAD_FILE_TIME_OUT = 58
    CANNOT_FOUND_SPECIFY_FILE = 59
    PARSE_JSON_FAIL = 60
    UNRAR_FILE_FAIL = 61
    LOAD_LOADER_FAIL = 62
    START_TEST_FAIL = 63
    GET_FILE_VERSION_FAIL = 64
    FILE_VERSION_NOT_EQUAL = 65
    NOT_SPECIFY_FILE = 66
    CANNOT_FOUND_SPECIFY_WINDOW = 67
    GET_DEVICE_INFO_FAIL = 68
    GET_PROC_FAIL = 69
    NOT_FOUND_RAR_FILE = 70
    CANNOT_FOUND_SPECIFY_LOGICAL_LETTER = 71
    GET_SERIAL_FAIL = 72
    CANNOT_FOUND_SPECIFY_PORT = 73
    CANNOT_FOUND_LOGICAL_DEVICE = 74
    ENUM_PROCESS_FAIL = 75
    IOMETER_ERROR = 76
    GET_MOUNT_POINT_FAIL = 77
    MOUNT_FAIL = 78
    NO_POWER_DEVICE = 79
    PROGRAM_ABORTED = 80
    DOWNLOAD_FILE_CONTENT_NOT_EQUAL = 81
    CONNECT_TOOL_FAIL = 82
    UNKNOWN_DECOMPRESSION_TYPE = 83
    UNZIP_FAIL = 84
    ABNORMAL_END = 85


class ErrorCode(Singleton):
    def __init__(self) -> None:
        super().__init__()
        self.status_code = {}
        self.error_code = {}
        self.load()

    def load(self, configPath=""):
        if not configPath:
            configPath = "config/ErrorStr.txt"

        with open(configPath, "r") as f:
            strs = ""
            isStatusCode = False
            isErrorCode = False
            for str in f.readlines():
                if -1 != str.find("[StatusCode]"):
                    isStatusCode = True
                    isErrorCode = False
                    continue
                elif -1 != str.find("[ErrorCode]"):
                    isStatusCode = False
                    isErrorCode = True
                    continue
                str = str.strip()
                if (index := str.find(" ")) == -1:
                    continue
                key = int(str[:index])
                value = str[index:]
                value = value.strip()
                if isStatusCode:
                    self.status_code[key] = value
                elif isErrorCode:
                    self.error_code[key] = value

    @staticmethod
    def getAllCode(statusCode: int, errorCode: int) -> int:
        all_code = (statusCode << 8) | errorCode
        return all_code

    def getAllStatus(self, statusCode: int, errorCode: int) -> str:
        state = self.getStatusStr(statusCode)
        error = self.getErrorStr(errorCode)
        all_state = ""
        if not state:
            all_state = error
        elif not error:
            all_state = f"{state} fail"
        else:
            all_state = f"{state},{error}"

        return all_state

    def getErrorStr(self, code: int) -> str:
        if code in self.error_code:
            return self.error_code[code]

        return ""

    def getStatusStr(self, code: int) -> str:
        if code in self.status_code:
            return self.status_code[code]

        return ""



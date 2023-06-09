import json
import struct
import cmpCommand.define



# 共享数据
class CMP_INFO_SHARE:
    def __init__(self, wNetPort: int , dwPortNumber: int, strLogDir: str):
        self.wNetPort = wNetPort
        self.dwPortNumber = dwPortNumber
        self.strLogDir = strLogDir

    def getbytes(self):
        data = struct.pack(cmpCommand.define._PACK_FORMAT_STR,  self.wNetPort, self.dwPortNumber,self.strLogDir.encode('utf8'))

        if len(data) % 4 != 0:
            data += bytes(4 - len(data) % 4)
        return data

    @staticmethod
    def parse(data):
        value = struct.unpack(cmpCommand.define._PACK_FORMAT_STR, data)
        share_info = CMP_INFO_SHARE(value[0], value[1], value[2].decode("utf8").replace("\0", ""))
        return share_info


# TCP数据包
class CMPHeader:
    _PACK_FORMAT_STR = "2i4b4s"
    def __init__(self, header):
        if header is None:
            self.flag = cmpCommand.define.NCMD_FLAG
            self.length = 0
            self.cmd = 0
            self.sub_cmd = 0
            self.packet_type = 0
            self.ack_type = 0
            self.resv = ""
        else:
            self.flag = header.flag
            self.length = header.length
            self.cmd = header.cmd
            self.sub_cmd = header.sub_cmd
            self.packet_type = header.packet_type
            self.ack_type = header.ack_type
            self.resv = header.resv

    @staticmethod
    def getHeaderLen():
        return struct.calcsize(CMPHeader._PACK_FORMAT_STR)

    def getBytes(self):
        data = struct.pack(self._PACK_FORMAT_STR, self.flag, self.length,  self.cmd,
                           self.sub_cmd, self.packet_type, self.ack_type, self.resv.encode("utf8"))
        return data

    @staticmethod
    def parse(data):
        packet_tuple = struct.unpack(CMPHeader._PACK_FORMAT_STR, data)
        header = CMPHeader(None)
        header.flag = packet_tuple[0]
        header.length = packet_tuple[1]
        header.cmd = packet_tuple[2]
        header.sub_cmd = packet_tuple[3]
        header.packet_type = packet_tuple[4]
        header.ack_type = packet_tuple[5]
        header.resv = packet_tuple[6]
        return header

class CMPDeviceStatus(object):
    CurrentCycles = 0  # 当前测试次数
    ErrorTimes = 0  # 当前错误次数
    ErrorCode = 0  # 错误代码
    CurrentPos = 0  # 当前进度
    TotalPos = 0  # 总进度
    Run = False  # 测试是否正在运行
    Finished = False  # 测试是否完成
    WorkType = ""  # 工作类型字符串，如BurnIn,h2test
    Speed = ""  # 当前磁盘的读写速度
    Status = ""  # 当前测试状态
    ExtraInfo = {}  # 额外测试信息,字典类型，key与value必须为字符串

# 测试状态
class CMP_DEVICE_STATUS:
    def __init__(self, status=None):
        if status is None:
            self.nSize = 0
            self.dwCurrentCycles = 0
            self.dwErrorTimes = 0
            self.dwErrorCode = 0
            self.ullCurrentPos = 0
            self.ullTotalPos = 0
            self.bRun = False
            self.bFinished = False
            self.strWorkType = ""
            self.strSpeed = ""
            self.strStatus = ""
            self.strExtraInfo = {}
        else:
            self.nSize = 0
            self.dwCurrentCycles = status.CurrentCycles
            self.dwErrorTimes = status.ErrorTimes
            self.dwErrorCode = status.ErrorCode
            self.ullCurrentPos = status.CurrentPos
            self.ullTotalPos = status.TotalPos
            self.bRun = status.Run
            self.bFinished = status.Finished
            self.strWorkType = status.WorkType
            self.strSpeed = status.Speed
            self.strStatus = status.Status
            self.strExtraInfo = status.ExtraInfo

    def toJsonDict(self):
        info = {}
        info["nSize"] = self.nSize
        info["dwCurrentCycles"] = self.dwCurrentCycles
        info["dwErrorTimes"] = self.dwErrorTimes
        info["dwErrorCode"] = self.dwErrorCode
        info["ullCurrentPos"] = self.ullCurrentPos
        info["ullTotalPos"] = self.ullTotalPos
        info["bRun"] = self.bRun
        info["bFinished"] = self.bFinished
        info["strWorkType"] = self.strWorkType
        info["strSpeed"] = self.strSpeed
        info["strStatus"] = self.strStatus
        info["strExtraInfo"] = self.strExtraInfo
        return info

    def toJson(self):
        info = self.toJsonDict()
        return json.dumps(info)

    def toBytes(self, nItem):
        nItem_data = struct.pack("i", nItem)
        reserve_data = struct.pack("i", 0)
        nSize_data = struct.pack("i", self.nSize)
        bRun_data = struct.pack("?", self.bRun)
        bFinish_data = struct.pack("?", self.bFinished)
        bReservel1_data = struct.pack("B", 0)
        bReservel2_data = struct.pack("B", 0)
        dwCurrentCycle_data = struct.pack("I", self.dwCurrentCycles)
        dwErrorTimes_data = struct.pack("I", self.dwErrorTimes)
        dwErrorCode_data = struct.pack("I", self.dwErrorCode)
        dwReserve_data = struct.pack("I", 0)
        ullCurrentPos_data = struct.pack("Q", self.ullCurrentPos)
        ullTotalPos_data = struct.pack("Q", self.ullTotalPos)

        strWorkType_data = struct.pack("40s", self.strWorkType.encode("utf8"))
        strSpeed_data = struct.pack("20s", self.strSpeed.encode("utf8"))
        strStatus_data = struct.pack("260s", self.strStatus.encode("utf8"))
        strExtraInfo_value = ""
        print("ExtraInfo:",self.strExtraInfo)
        for key, value in self.strExtraInfo.items():
            try:
                data = f"{key}:{value}\n"
                value += data
            except:
                pass
        if len(strExtraInfo_value) >= 1:
            if strExtraInfo_value[-1] == "\n":
                strExtraInfo_value[-1] = ""
        strExtraInfo_data = struct.pack(f"{len(strExtraInfo_value.encode('utf8'))}s", strExtraInfo_value.encode('utf8'))
        data = nItem_data + reserve_data + nSize_data + bRun_data + bFinish_data + bReservel1_data + bReservel2_data \
               + dwCurrentCycle_data + dwErrorTimes_data + dwErrorCode_data + dwReserve_data + ullCurrentPos_data +\
               ullTotalPos_data + strWorkType_data + strSpeed_data + strStatus_data + strExtraInfo_data
        return data




    @staticmethod
    def parse(data):
        if isinstance(data, bytes):
            datalen = struct.calcsize("3i2?2B4I2Q40s20s260s")
            extrainfo_lenght= len(data) - datalen
            status_data = struct.unpack(f"3i2?2B4I2Q40s20s260s{extrainfo_lenght}s", data)
            # status_data = struct.unpack("2i?3I", data[4:28])
            # status_pos = struct.unpack("2Q", data[32:48])  #
            # status_runAndFinish = struct.unpack("2?", data[48:50])
            # status_status = struct.unpack("1040s", data[208:1248])[0].decode("utf32").replace("\0", "")
            # status_extrainfo = struct.unpack(f"{len(data) - 1248}s", data[1248:])[0].decode(
            #     "utf32").replace("\0", "").split("\n")
            status_extrainfo = status_data[16].decode("utf8").replace("\0", "").split("\n")
            status_extrainfo_list = {}
            for extrainfo in status_extrainfo:
                if ":" in extrainfo:
                    key, value = extrainfo.split(":", 1)
                    status_extrainfo_list[key] = value
            info = {
                "nSize": status_data[2],
                "bRun": status_data[3],
                "bFinished": status_data[4],
                "dwCurrentCycles": status_data[7],
                "dwErrorTimes": status_data[8],
                "dwErrorCode": status_data[9],
                "ullCurrentPos": status_data[11],
                "ullTotalPos": status_data[12],
                "strWorkType": status_data[13].decode("utf8").replace("\0", ""),
                "strSpeed": status_data[14].decode("utf8").replace("\0", ""),
                "strStatus": status_data[15].decode("utf8").replace("\0", ""),
                "strExtraInfo": status_extrainfo_list
            }
            print(info)
            device_cmd = CMP_DEVICE_STATUS(None)
            device_cmd.nSize = info["nSize"]
            device_cmd.dwCurrentCycles = info["dwCurrentCycles"]
            device_cmd.dwErrorTimes = info["dwErrorTimes"]
            device_cmd.dwErrorCode = info["dwErrorCode"]
            device_cmd.ullCurrentPos = info["ullCurrentPos"]
            device_cmd.ullTotalPos = info["ullTotalPos"]
            device_cmd.bRun = info["bRun"]
            device_cmd.bFinished = info["bFinished"]
            device_cmd.strWorkTye = info["strWorkType"]
            device_cmd.strSpeed = info["strSpeed"]
            device_cmd.strStatus = info["strStatus"]
            device_cmd.strExtraInfo = info["strExtraInfo"]
            return device_cmd
        else:
            device_cmd = CMP_DEVICE_STATUS(None)
            info = json.loads(data)
            device_cmd.nSize = info["nSize"]
            device_cmd.dwCurrentCycles = info["dwCurrentCycles"]
            device_cmd.dwErrorTimes = info["dwErrorTimes"]
            device_cmd.dwErrorCode = info["dwErrorCode"]
            device_cmd.ullCurrentPos = info["ullCurrentPos"]
            device_cmd.ullTotalPos = info["ullTotalPos"]
            device_cmd.bRun = info["bRun"]
            device_cmd.bFinished = info["bFinished"]
            device_cmd.strWorkTye = info["strWorkType"]
            device_cmd.strSpeed = info["strSpeed"]
            device_cmd.strStatus = info["strStatus"]
            device_cmd.strExtraInfo = info["strExtraInfo"]
            return device_cmd



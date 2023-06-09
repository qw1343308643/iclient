

def log_header_templete(headerList: list):
    print("headerList:",headerList)
    header = f"""
    SN:             {headerList[0]}
    Result:               {headerList[1]}
    Error Code:             {headerList[2]}
    Mac Addr:               {headerList[3]}
    Disk:               {headerList[4]}
    Index:              {headerList[5]}
    FW Version:             {headerList[6]}
    ModelName:              {headerList[7]}
    Capacity:               {headerList[8]}
    StartTime:              {headerList[9]}
    EndTime:                {headerList[10]}
    TotalCycle"             {headerList[11]}"""
    return header


def log_result_templete(param: dict):
    print("param:",param)
    log_result = f"""
    *******************************************
    ===================================================
    item:{param[0]}
    *********************
    Configuration Information
    ConfigFile             {param[1]}
    *********************
    DETAILED EVENT LOG
    *********************

    *********************
    RESULT SUMMARY
    *********************
    Start Time:             {param[2]}
    Stop Time:              {param[3]}
    Test Duration:              {str(param[4])}
    Error Times:                {param[5]}
    Result:             {param[6]}
    ErrorCode:              {param[7]}\n\n"""
    return log_result
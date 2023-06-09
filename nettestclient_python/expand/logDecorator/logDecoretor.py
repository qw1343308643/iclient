import inspect
import logging
import time
import traceback
import os
import sys

import logging
import os
from logging.handlers import RotatingFileHandler

class FileterPrint(logging.Filter):
    def filter(self, record):
        return "Sending ping" not in record.msg

class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
        return t

class LogPrint:
    def __init__(self, logger):
        self.logger = logger

    def write(self, msg):
        if msg.strip():
            frame = inspect.currentframe().f_back
            filename = inspect.getframeinfo(frame).filename
            funcname = inspect.getframeinfo(frame).function
            lineno = inspect.getframeinfo(frame).lineno
            log_msg = f"[{filename} - {funcname} - line {lineno}] {msg.strip()}"
            self.logger.info(log_msg)

class CustomLogger(object):
    def __init__(self, fpath):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        formatter = CustomFormatter('%(asctime)s - %(levelname)s - %(message)s')
        # log_print = LogPrint(self.logger)
        # sys.stdout.write = log_print.write

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(FileterPrint())
        self.logger.addHandler(console_handler)

        if not os.path.exists(fpath):
            os.makedirs(fpath)

        path = os.path.join(fpath, "logDebug.txt")

        file_handler = RotatingFileHandler(path, mode='a+', encoding='utf-8', maxBytes=1024 * 1024 * 100, backupCount=5)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def write(self, msg):
        if msg.strip():
            self.logger.info(msg.strip())


    def flush(self):
        pass

    def close(self):
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)



class LoggerPrint(object):
    def __init__(self, fpath):
        self.console = sys.stdout
        self.file = None
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        path = os.path.join(fpath, "logDebug.txt")
        self.file = open(path, 'a+')

    def __del__(self):
        self.close()
        self.file.close()

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.close()
        self.file.close()

    def write(self, msg):
        self.console.write(msg)
        if self.file is not None:
            if len(msg) != 0:
                self.file.write(f"{str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))}:{msg}\n")

    def flush(self):
        self.console.flush()
        if self.file is not None:
            self.file.flush()
            os.fsync(self.file.fileno())

    def close(self):
        self.console.close()
        if self.file is not None:
            self.file.close()


import inspect
import logging
import time
import traceback
import os
import sys


class ClientLog():
    pass

def debug(func):
    # 获取日志记录器, 记录日志等级
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.setLevel('DEBUG')
    # 设置日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s")
    # 输出到控制台的handler
    ch = logging.StreamHandler()
    # 配置默认日志格式
    ch.setFormatter(formatter)
    # 日志记录器增加到handler
    logger.addHandler(ch)
    # 输出到文件
    dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
    log_dir = os.path.join(dirname, "temp/Data/Debug")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, "debug.log")
    file_handler = logging.FileHandler(log_path, encoding="utf8")
    file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
    logger.addHandler(file_handler)
    def inner(*args, **kwargs):
        try:
            # timestamp = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
            res = func(*args, **kwargs)
            logger.debug(f"{func.__name__} - > {args, kwargs}")
            return res
        except Exception as e:
            logger.error(f"error:{func.__name__},meesage:{traceback.format_exc()}")
    return inner



class LoggerPrint(object):
    def __init__(self, fpath):
        self.console = sys.stdout
        self.file = None
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        path = os.path.join(fpath, "logDebug.txt")
        self.file = open(path, 'w')

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


class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log(self, message, level=logging.INFO):
        if level == logging.ERROR:
            self.logger.exception(message)
        else:
            self.logger.log(level, message)


def log(cls):
    class LoggedClass(cls):
        def __getattribute__(self, name):
            attr = super().__getattribute__(name)
            if callable(attr) and not name.startswith('_'):  # 忽略私有方法和特殊方法（如__init__）
                def wrapper(*args, **kwargs):
                    logger = Logger(self.__class__.__name__)
                    logger.log(f"Entering {name}()...", level=logging.DEBUG)

                    try:
                        result = attr(*args, **kwargs)
                        logger.log(f"Leaving {name}()...", level=logging.DEBUG)

                        return result

                    except Exception as e:
                        logger.log(f"Error in {name}(): {str(e)}", level=logging.ERROR)

                return wrapper
            else:  # 非函数属性直接返回
                return attr

    return LoggedClass


def log_all_methods(cls):
    for name, method in inspect.getmembers(cls, inspect.isfunction):  # 获取所有函数属性
        setattr(cls, name, log(method))  # 为每个函数属性添加日志记录功能
    return cls

# coding=utf-8

'''
文件锁
'''
import os.path
import platform
import time

fcntl = None
msvcrt = None
bLinux = True
if platform.system() != 'Windows':
    fcntl = __import__("fcntl")
    bLinux = True
else:
    msvcrt = __import__('msvcrt')
    bLinux = False


# 文件锁
class CFileLock:
    def __init__(self, filename):
        self.filename = filename + '.lock'
        self.handle = None

    # 文件锁
    def acquire(self):
        while 1:
            if os.path.exists(self.filename):
                try:
                    self.handle = open(self.filename, "r")
                    fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return True
                except IOError:
                    self.handle.close()
            else:
                try:
                    self.handle = open(self.filename, "w")
                    fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return True
                except IOError:
                    self.handle.close()
            time.sleep(0.1)

    def release(self):
        if self.handle is not None:
            fcntl.flock(self.handle, fcntl.LOCK_UN)
            self.handle.close()
            os.remove(self.filename)
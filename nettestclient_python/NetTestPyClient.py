import atexit
import os
import signal
import subprocess
import sys
import time
import traceback

def checkProcess():
    cur_pid = str(os.getpid())
    print("current client pid:",cur_pid)
    cmd = "ps -ef | grep NetTestPyClient.py | grep -v grep | awk '{print $2}'"
    ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    pids = ret.stdout.read().decode().split("\n")
    print(pids)
    if len(pids) >= 3:
        return False
    return True

def signal_exit(signum, frame):
    text = f"catch signal:{signum}"
    with open("error.log", "a") as f:
        f.write(f"{str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))}:{str(text)}\n")
    sys.exit(0)


def handle_exception(exc_type=None, exc_value=None, exc_traceback=None):
    traceback_str = traceback.format_exc()
    print("traceback_str:", traceback_str)
    with open("error.log", "a") as f:
        f.write(f"{str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))}:{str(traceback_str)}")

if __name__ == '__main__':
    try:
        from PyClientMain import main
        # sys.excepthook = handle_exception
        # signal.signal(signal.SIGTERM, signal_exit)
        # signal.signal(signal.SIGINT, signal_exit)
        ret = checkProcess()
        if ret:
            main()
        else:
            print("The client has started and cannot run the second one")
    except Exception as e:
        print(e)
        # handle_exception()
        text = f"meesage:{traceback.format_exc()}"
        dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
        Path = "error.txt"
        errorPath = os.path.join(dirname, Path)
        with open(errorPath, "w") as f:
            f.write(text)

# i am new code
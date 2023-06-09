import os
from multiprocessing import shared_memory


def clearUp(share_name):
    try:
        shm_a = shared_memory.SharedMemory(name=share_name, create=False, size=268)
        shm_a.unlink()
    except Exception as e:
        print("delShareInfo:", e)
    path = os.path.join("/data/tmp/boost_interprocess", share_name)
    if os.path.exists(path):
        os.remove(path)

import time, threading
def fromMainThread():
    return "called from main thread"

def fromOtherThread():
    return "called from other thread"

def neverCalled():
    return "no one calls me"

threading.Thread(target=fromOtherThread).start()
fromMainThread()
time.sleep(1)

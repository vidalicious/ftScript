# import Queuefrom datetime import *
import datetime
import time
import threading
# a = time(22, 34, 0000)
# b = datetime.now().time()
threadPool = []
print datetime.datetime.now().time() > datetime.time(15, 58, 0)

def a():
    while True:
        print "aaa"
        time.sleep(1)

def b():
    while True:
        print "bbb"
        time.sleep(2)

t1 = threading.Thread(target=a)
t2 = threading.Thread(target=b)
threadPool.append(t1)
threadPool.append(t2)

t1.setDaemon(True)
t1.start()
while True:

    print "ccc"

#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *

host = "localhost"
port = 11111

targetCode = "800000" # 恒指

bullCode = "65205"
bearCode = "64940"

oneTickTime = 1
counter = 0

connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        file = open("bull and bear data", "a+")

        targetPrice = getCurrentPrice(connectSocket, targetCode)
        print "target ", targetCode, " currentPrice ", floatPrice(targetPrice), " count ", counter, " time ", time.strftime('%Y-%m-%d %H:%M:%S')
        log = ["target ", targetCode, " currentPrice ", str(floatPrice(targetPrice)), " count ", str(counter), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"]
        file.writelines(log)

        bullPrice = getCurrentPrice(connectSocket, bullCode)
        print "bull ", bullCode, " current price ", floatPrice(bullPrice)
        log = ["bull ", bullCode, " current price ", str(floatPrice(bullPrice)), "\n"]
        file.writelines(log)

        bearPrice = getCurrentPrice(connectSocket, bearCode)
        print "bear ", bearCode, " current price ", floatPrice(bearPrice)
        log = ["bear ", bearCode, " current price ", str(floatPrice(bearPrice)), "\n"]
        file.writelines(log)

        log = ["==========================================================================================\n"]
        file.writelines(log)

        file.close()
        counter += 1
        time.sleep(oneTickTime)
    disconnect(connectSocket)
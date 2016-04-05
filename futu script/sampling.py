#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import FSApi
import time

host = "localhost"
port = 11111
stockCode = "01419"
tradeOneHand = 2000

count = 0
connectSocket = FSApi.connect(host, port)
if connectSocket is not None:
    while True:
        currentPrice = FSApi.getCurrentPrice(connectSocket, stockCode)
        print "currentPrice ", float(currentPrice) / 1000, " count ", count, " time ", time.strftime('%Y-%m-%d %H:%M:%S')
        log = ["currentPrice ", str(float(currentPrice) / 1000), " count ", str(count), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"]
        file = open("data", "a+")
        file.writelines(log)
        file.close()
        count += 1
        time.sleep(1)
FSApi.disconnect(connectSocket)
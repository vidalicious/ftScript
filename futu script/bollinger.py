#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import FSApi
import time
from FSApi import *
from math import *

host = "localhost"
port = 11111
stockCode = "01419"
tradeOneHand = 2000

counter = 0

# 均值
mean = 0
# 方差
variance = 0
# 标准差
standardDeviation = 0

bollingRadius = 2 #2倍标准差

connectSocket = FSApi.connect(host, port)
if connectSocket is not None:
    while True:
        currentPrice = FSApi.getCurrentPrice(connectSocket, stockCode)
        print "currentPrice", float(currentPrice) / 1000, "counter", counter, "time", time.strftime('%Y-%m-%d %H:%M:%S')

        mean = (mean * counter + floatPrice(currentPrice)) / (counter + 1)
        variance = (variance * counter + (floatPrice(currentPrice) - mean) ** 2) / (counter + 1)
        standardDeviation = sqrt(variance)

        if floatPrice(currentPrice) > mean + bollingRadius * standardDeviation:#顶端

        elif 

        counter += 1
FSApi.disconnect(connectSocket)
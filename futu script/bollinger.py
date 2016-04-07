#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import FSApi
import time
from FSApi import *
from math import *

# ====================== config =================
oneTickTime = 3
bollingRadius = 2 # 2倍标准差

host = "localhost"
port = 11111
stockCode = "01419"
tradeOneHand = 2000

shortMovingTicks = 5
longMovingTicks = 20
# ===================================================
counter = 0

# 均值
mean = 0
# 方差
variance = 0
# 标准差
standardDeviation = 0

lastPrice = 0

shortTickList = []
longTickList = []

shortMAList = []
longMAList = []

connectSocket = FSApi.connect(host, port)
if connectSocket is not None:
    while True:
        currentPrice = FSApi.getCurrentPrice(connectSocket, stockCode)
        print "currentPrice", floatPrice(currentPrice), "counter", counter, "time", time.strftime('%Y-%m-%d %H:%M:%S')

        # ============= moving average ================

        shortTickList.insert(0, floatPrice(currentPrice))
        if len(shortTickList) > shortMovingTicks:
            shortTickList = shortTickList[:shortMovingTicks]

        longTickList.insert(0, floatPrice(currentPrice))
        if len(longTickList) > longMovingTicks:
            longTickList = longTickList[:longMovingTicks]

        shortMAList.insert(0, getAveragePriceFromList(shortTickList))
        if len(shortMAList) > 5:
            shortMAList = shortMAList[:5]

        longMAList.insert(0, getAveragePriceFromList(longTickList))
        if len(longMAList) > 5:
            longMAList = longMAList[:5]

        # ============== bollinger =================
        mean = (mean * counter + floatPrice(currentPrice)) / (counter + 1)
        variance = (variance * counter + (floatPrice(currentPrice) - mean) ** 2) / (counter + 1)
        standardDeviation = sqrt(variance)

        if floatPrice(currentPrice) > mean + bollingRadius * standardDeviation: #顶端
            pass
        elif floatPrice(currentPrice) > mean - bollingRadius * standardDeviation\
                and floatPrice(currentPrice) <= mean + bollingRadius * standardDeviation: # 带中
            pass
        else: #底部
            pass

        # 更新价格
        lastPrice = currentPrice
        counter += 1
        time.sleep(oneTickTime)
FSApi.disconnect(connectSocket)
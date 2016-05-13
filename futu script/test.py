#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from FSApi import *

host = "localhost"
port = 11111
stockCode = "00500"

count = 0
connectSocket = connect(host, port)
if connectSocket is not None:
    # while True:
    # file = open("run log", "a+")
    # currentPrice = FSApi.getCurrentPrice(connectSocket, stockCode)
    # # sell_one = FSApi.getSellPrice(connectSocket, stockCode, 1, 0)
    # # localID = FSApi.simu_commonBuyOrder(connectSocket, sell_one, 1000, stockCode)
    # # FSApi.simu_setOrderStatus(connectSocket, 0, 0, 0)
    # buy_one = FSApi.getBuyPrice(connectSocket, stockCode, 1, 0)
    # localID = FSApi.simu_commonSellOrder(connectSocket, buy_one, 1000, stockCode)
    # buyPrice = FSApi.getBuyPrice(connectSocket, stockCode, 3, 0)
    # buy2 = FSApi.getBuyPrice(connectSocket, stockCode, 3, 1)
    # buy3 = FSApi.getBuyPrice(connectSocket, stockCode, 3, 2)
    # if currentPrice is not None:
    #     print currentPrice, count , buyPrice, buy_one
    #     l = [currentPrice, str(count), buyPrice, "\n"]
    #     file.writelines(l)
    #     count += 1
    bullCode = "63025"
    positionArr = simu_inquirePosition(connectSocket)
    hasBullPosition = ifHasPositon(positionArr, bullCode)

    # file.close()

disconnect(connectSocket)

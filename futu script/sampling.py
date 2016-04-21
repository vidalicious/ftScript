#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from FSApi import *
import time
from math import *

host = "localhost"
port = 11111
stockCode = "01157"
tradeOneHand = 200

oneTickTime = 3
counter = 0

# 均值
mean = 0
# 方差
variance = 0
# 标准差
standardDeviation = 0

connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        file = open("data", "a+")
        # =============== current price =================
        currentPrice = getCurrentPrice(connectSocket, stockCode)
        print "stock ", stockCode, " currentPrice ", float(currentPrice) / 1000, " count ", counter, " time ", time.strftime('%Y-%m-%d %H:%M:%S')
        log = ["stock ", stockCode, " currentPrice ", str(float(currentPrice) / 1000), " count ", str(counter), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"]
        file.writelines(log)

        # # =============== buy and sell ==================
        #
        # gearArr = getGearData(connectSocket, stockCode, 10)
        #
        # buyOrder = []
        # buyPrice = []
        # buyVol = []
        #
        # sellOrder = []
        # sellPrice = []
        # sellVol = []
        #
        # if gearArr is not None:
        #     for gear in gearArr:
        #         buyOrder.append(gear["BuyOrder"])
        #         buyPrice.append(gear["BuyPrice"])
        #         buyVol.append(gear["BuyVol"])
        #
        #         sellOrder.append(gear["SellOrder"])
        #         sellPrice.append(gear["SellPrice"])
        #         sellVol.append(gear["SellVol"])
        #
        # if buyPrice is not None:
        #     for i in range(len(sellPrice))[::-1]:
        #         print "sell ", i + 1, " order ", sellOrder[i], " price ", floatPrice(sellPrice[i]), " vol ", sellVol[i]
        #         log = ["sell ", str(i + 1), " order ", sellOrder[i], " price ", str(floatPrice(sellPrice[i])), " vol ", sellVol[i], "\n"]
        #         file.writelines(log)
        #
        #     print "-- mid gear price ", (floatPrice(buyPrice[0]) + floatPrice(sellPrice[0])) / 2
        #     log = ["-- mid gear price ", str((floatPrice(buyPrice[0]) + floatPrice(sellPrice[0])) / 2), "\n"]
        #     file.writelines(log)
        #
        #     for i in range(len(buyPrice)):
        #         print "buy ", i + 1, " order ", buyOrder[i], " price ", floatPrice(buyPrice[i]), " vol ", buyVol[i]
        #         log = ["buy ", str(i + 1), " order ", buyOrder[i], " price ", str(floatPrice(buyPrice[i])), " vol ", buyVol[i], "\n"]
        #         file.writelines(log)
        #
        #
        #
        #     log = ["==========================================================================================\n"]
        #     file.writelines(log)

        # ============== bollinger =================
        mean = (mean * counter + floatPrice(currentPrice)) / (counter + 1)
        variance = (variance * counter + (floatPrice(currentPrice) - mean) ** 2) / (counter + 1)
        standardDeviation = sqrt(variance)

        print "mean ", mean, " standard deviation ", standardDeviation
        log = ["mean ", str(mean), " standard deviation ", str(standardDeviation), "\n"]
        file.writelines(log)

        if standardDeviation != 0:
            print "current price is ", str((floatPrice(currentPrice) - mean) / standardDeviation), " standard deviation to mean"
            log = ["current price is ", str((floatPrice(currentPrice) - mean) / standardDeviation), " standard deviation to mean"]
            file.writelines(log)
        else:
            print "standard deviation is 0"
            log = "standard deviation is 0"
            file.writelines(log)

        file.close()
        counter += 1
        time.sleep(oneTickTime)
disconnect(connectSocket)
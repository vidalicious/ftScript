#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *

host = "localhost"
port = 11111

targetCode = "800000" # 恒指

bullCode = "65319"
bearCode = "65281"

oneTickTime = 1
counter = 0

movingAverageCount = 60 / oneTickTime # 1分钟的tick数

targetList = []

# 均值
mean = 0
# 方差
variance = 0
# 标准差
standardDeviation = 0

maxAwaySD = 0

connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        file = open("bull and bear data", "a+")

        currentTarget = getCurrentPrice(connectSocket, targetCode)
        print "counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')
        logger = ["counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"]
        file.writelines(logger)

        targetList.insert(0, floatPrice(currentTarget))
        if len(targetList) > movingAverageCount:
            targetList = targetList[:movingAverageCount]

        mean = getMeanFromList(targetList)
        variance = getVarianceFromList(targetList, mean)
        standardDeviation = sqrt(variance)
        if standardDeviation == 0:
            awaySD = 0
        else:
            awaySD = (floatPrice(currentTarget) - mean) / standardDeviation
        print "mean ", str(mean), " standard deviation ", str(standardDeviation), " current target to mean ", str(awaySD), " SD away"
        logger = ["mean ", str(mean), " standard deviation ", str(standardDeviation), " current target to mean ", str(awaySD), " SD away", "\n"]
        file.writelines(logger)
        if awaySD > maxAwaySD:
            maxAwaySD = awaySD
        print "max away SD ", str(maxAwaySD)
        logger = ["max away SD ", str(maxAwaySD), "\n"]
        file.writelines(logger)

        bullPrice = getCurrentPrice(connectSocket, bullCode)
        print "bull ", bullCode, " current price ", floatPrice(bullPrice)
        logger = ["bull ", bullCode, " current price ", str(floatPrice(bullPrice)), "\n"]
        file.writelines(logger)

        bearPrice = getCurrentPrice(connectSocket, bearCode)
        print "bear ", bearCode, " current price ", floatPrice(bearPrice)
        logger = ["bear ", bearCode, " current price ", str(floatPrice(bearPrice)), "\n"]
        file.writelines(logger)

        # # ========================== bull ================================
        # print "----------- bull gear -----------"
        # log = ["----------- bull gear -----------", "\n"]
        # file.writelines(log)
        #
        # gearArr = getGearData(connectSocket, bullCode, 10)
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
        # # ================= bear ===================
        # print "----------- bear gear -----------"
        # log = ["----------- bear gear -----------", "\n"]
        # file.writelines(log)
        #
        # gearArr = getGearData(connectSocket, bearCode, 10)
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


        log = ["==========================================================================================\n"]
        file.writelines(log)

        file.close()
        counter += 1
        time.sleep(oneTickTime)
    disconnect(connectSocket)
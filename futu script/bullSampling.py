#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *

host = "localhost"
port = 11111

# targetCode = "800000" # 恒指

bullCode = "63249"

oneTickTime = 1
counter = 0

ema1Count = 60 / oneTickTime # 1分钟的tick数
ema5Count = 60 * 5 / oneTickTime #5分钟tick
windowCount = 60
priceList = []

mean1 = 0
mean5 = 0

variance1 = 0
# 标准差
standardDeviation1 = 0

variance5 = 0
# 标准差
standardDeviation5 = 0

ema1_K = float(2.0 / (ema1Count + 1))
ema5_K = float(2.0 / (ema5Count + 1))

averageBias1 = 0
averageBias5 = 0

maxAwaySD = 0

connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        if datetime.datetime.now().time() > datetime.time(16, 0, 1):
            break

        file = open("bull data", "a+")
        
        currentBullPrice = getCurrentPrice(connectSocket, bullCode)
        print "counter ", str(counter), " bull ", str(floatPrice(currentBullPrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " bull code ", bullCode
        logger = ["counter ", str(counter), " bull ", str(floatPrice(currentBullPrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " bull code ", bullCode, "\n"]
        file.writelines(logger)
        
        priceList.insert(0, floatPrice(currentBullPrice))
        if len(priceList) > windowCount:
            priceList = priceList[:windowCount]

        if mean1 != 0:
            mean1 = floatPrice(currentBullPrice) * ema1_K + mean1 * (1 - ema1_K)
        else:
            mean1 = floatPrice(currentBullPrice)

        if mean5 != 0:
            mean5 = floatPrice(currentBullPrice) * ema5_K + mean5 * (1 - ema5_K)
        else:
            mean5 = floatPrice(currentBullPrice)

        variance1 = getVarianceFromList(priceList, mean1)
        standardDeviation1 = sqrt(variance1)

        variance5 = getVarianceFromList(priceList, mean5)
        standardDeviation5 = sqrt(variance5)

        averageBias1 = getAverageBiasFromList(priceList, mean1)
        averageBias5 = getAverageBiasFromList(priceList, mean5)

        meanBiasRate = (mean1 - mean5) / mean5

        print "mean bias rate ", str(meanBiasRate)
        logger = ["mean bias rate ", str(meanBiasRate), "\n"]
        file.writelines(logger)

        print "mean1 ", str(mean1), " standard deviation1 ", str(standardDeviation1), " average bias1 ", str(averageBias1)
        logger = ["mean1 ", str(mean1), " standard deviation1 ", str(standardDeviation1), " average bias1 ", str(averageBias1), "\n"]
        file.writelines(logger)

        print "mean5 ", str(mean5), " standard deviation5 ", str(standardDeviation5), " average bias5 ", str(averageBias5)
        logger = ["mean5 ", str(mean5), " standard deviation5 ", str(standardDeviation5), " average bias5 ", str(averageBias5), "\n"]
        file.writelines(logger)

        # bullPrice = getCurrentPrice(connectSocket, bullCode)
        # print "bull ", bullCode, " current price ", floatPrice(bullPrice)
        # logger = ["bull ", bullCode, " current price ", str(floatPrice(bullPrice)), "\n"]
        # file.writelines(logger)
        #
        # bearPrice = getCurrentPrice(connectSocket, bearCode)
        # print "bear ", bearCode, " current price ", floatPrice(bearPrice)
        # logger = ["bear ", bearCode, " current price ", str(floatPrice(bearPrice)), "\n"]
        # file.writelines(logger)

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
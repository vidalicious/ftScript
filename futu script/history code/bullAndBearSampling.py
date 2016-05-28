#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *

host = "localhost"
port = 11111

targetCode = "999000" # 恒指

bullCode = "65319"
bearCode = "65281"

oneTickTime = 3
counter = 0

ema10sCount = 10 / oneTickTime #10秒
ema1Count = 60 / oneTickTime # 1分钟的tick数
ema5Count = 60 * 5 / oneTickTime #5分钟tick
ema10Count = 60 * 10 / oneTickTime
ema15Count = 60 * 15 / oneTickTime
ema20Count = 60 * 20 / oneTickTime
ema30Count = 60 * 30 / oneTickTime
ema45Count = 60 * 45 / oneTickTime
ema60Count = 60 * 60 / oneTickTime

windowCount = 60
targetList = []

mean10s = 0
mean1 = 0
mean5 = 0
mean10 = 0
mean15 = 0
mean20 = 0
mean30 = 0
mean45 = 0
mean60 = 0

variance1 = 0
# 标准差
standardDeviation1 = 0

variance5 = 0
# 标准差
standardDeviation5 = 0

ema10s_K = float(2.0 / (ema10sCount + 1))
ema1_K = float(2.0 / (ema1Count + 1))
ema5_K = float(2.0 / (ema5Count + 1))
ema10_K = float(2.0 / (ema10Count + 1))
ema15_K = float(2.0 / (ema15Count + 1))
ema20_K = float(2.0 / (ema20Count + 1))
ema30_K = float(2.0 / (ema30Count + 1))
ema45_K = float(2.0 / (ema45Count + 1))
ema60_K = float(2.0 / (ema60Count + 1))

averageBias1 = 0
averageBias5 = 0

maxAwaySD = 0

connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        if not isGameBegin():
            continue
        elif datetime.datetime.now().time() > datetime.time(16, 0, 1):
            break

        file = open("bull and bear data.txt", "a+")

        currentTarget = getCurrentPrice(connectSocket, targetCode)
        print "counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')
        logger = ["counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"]
        file.writelines(logger)

        targetList.insert(0, floatPrice(currentTarget))
        if len(targetList) > windowCount:
            targetList = targetList[:windowCount]

        if mean10s != 0:
            mean10s = floatPrice(currentTarget) * ema10s_K + mean10s * (1 - ema10s_K)
        else:
            mean10s = floatPrice(currentTarget)

        if mean1 != 0:
            mean1 = floatPrice(currentTarget) * ema1_K + mean1 * (1 - ema1_K)
        else:
            mean1 = floatPrice(currentTarget)

        if mean5 != 0:
            mean5 = floatPrice(currentTarget) * ema5_K + mean5 * (1 - ema5_K)
        else:
            mean5 = floatPrice(currentTarget)

        mean10 = updateMeanBy(floatPrice(currentTarget), ema10_K, mean10)
        mean15 = updateMeanBy(floatPrice(currentTarget), ema15_K, mean15)
        mean20 = updateMeanBy(floatPrice(currentTarget), ema20_K, mean20)
        mean30 = updateMeanBy(floatPrice(currentTarget), ema30_K, mean30)
        mean45 = updateMeanBy(floatPrice(currentTarget), ema45_K, mean45)
        mean60 = updateMeanBy(floatPrice(currentTarget), ema60_K, mean60)

        variance1 = getVarianceFromList(targetList, mean1)
        standardDeviation1 = sqrt(variance1)

        variance5 = getVarianceFromList(targetList, mean5)
        standardDeviation5 = sqrt(variance5)

        averageBias1 = getAverageBiasFromList(targetList, mean1)
        averageBias5 = getAverageBiasFromList(targetList, mean5)

        meanBiasRate = (mean1 - mean5) / mean5

        print "mean10s ", str(mean10s), " mean1 ", str(mean1), " mean5 ", str(mean5)
        logger = ["mean10s ", str(mean10s), " mean1 ", str(mean1), " mean5 ", str(mean5), "\n"]
        file.writelines(logger)

        print "mean10s - mean1 ", str(mean10s - mean1), " mean10s - mean5 ", str(mean10s - mean5), " mean1 - mean5 ", str(mean1 - mean5)
        logger = ["mean10s - mean1 ", str(mean10s - mean1), " mean10s - mean5 ", str(mean10s - mean5), " mean1 - mean5 ", str(mean1 - mean5), "\n"]
        file.writelines(logger)

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
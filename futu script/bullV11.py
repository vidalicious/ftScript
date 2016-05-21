#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *
import datetime
import threading

# 恒指瑞银七二牛   63331   19650

# greed is good
# ==================== config =========================
oneTickTime = 10

host = "localhost"
port = 11111

targetCode = "999000" # 恒指
bullCode = "63331"
indexCode = "800000"
bullRecyclePrice = 19650
tradeOneHand = 10000

ema2Count = 60 * 2 / oneTickTime
ema5Count = 60 * 5 / oneTickTime #5分钟tick

windowCount = 60
# =========================================================
counter = 0

mean2 = 0
mean5 = 0

lastMean2 = 0
lastMean5 = 0

ema2_K = float(2.0 / (ema2Count + 1))
ema5_K = float(2.0 / (ema5Count + 1))

pathTag = []

flag = False

# ================ trigger ========================
def trigger():
    global flag
    while True:
        flag = True
        time.sleep(oneTickTime)
# ==========================================================
triggerThread = threading.Thread(target=trigger)
triggerThread.setDaemon(True)
triggerThread.start()
connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        if not isGameBegin():
            # print "game not begin"
            continue
        elif isTimeToExit():
            print "time to exit"
            break

        file = open("bullAndBearLog.txt", "a+")

        # ========== moving average ================
        currentTarget = getCurrentPrice(connectSocket, targetCode)
        print "counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')

        indexPrice = getCurrentPrice(connectSocket, indexCode)
        print "index price ", str(indexPrice)

        if flag: # one tick 触发一次
            flag = False

            mean2 = updateMeanBy(floatPrice(currentTarget), ema2_K, mean2)
            mean5 = updateMeanBy(floatPrice(currentTarget), ema5_K, mean5)

            print "mean2", str(mean2), " mean5 ", str(mean5)
            counter += 1

        if counter > windowCount:

            pathTag.extend(["counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"])
            pathTag.extend(["mean2", str(mean2), " mean5 ", str(mean5), "\n"])

            bullBuy1Price = ""
            bullSell1Price = ""
            bullGearArr = getGearData(connectSocket, bullCode, 1)
            if bullGearArr is not None:
                bullBuy1Price = bullGearArr[0]["BuyPrice"]
                bullSell1Price = bullGearArr[0]["SellPrice"]

            # ============== inquire position =====================
            positionArr = simu_inquirePosition(connectSocket)
            hasBullPosition = ifHasPositon(positionArr, bullCode)
            positionCost = getPositionPrice(positionArr, bullCode)
            positionQty = getPositionQty(positionArr, bullCode)
            positionRatio = getPositionRatio(positionArr, bullCode)

            print "hasBullPosition ", hasBullPosition

            # ============== inquire order ========================

            if hasBullPosition:
                if isInWarningTime():
                    tradePrice = bullBuy1Price
                    pathTag.append(" 4 ")
                    print "d"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bullCode, file, pathTag)

                elif lastMean2 >= lastMean5 and mean2 < mean5:
                    tradePrice = bullBuy1Price
                    pathTag.append(" 1 ")
                    print "a"

                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bullCode, file, pathTag)

                elif positionRatio < -0.03:
                    tradePrice = bullBuy1Price
                    pathTag.append(" 3 ")
                    print "c"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bullCode, file, pathTag)

            else:
                if abs(floatPrice(indexPrice) - bullRecyclePrice) < 300:
                    print "too near recycle price"
                elif not isInGoldenTime():
                    pathTag.append(" not in golden time ")
                    print "not in golden time"
                else:
                    if lastMean2 <= lastMean5 and mean2 > mean5:
                        tradePrice = bullSell1Price
                        pathTag.append(" 6 ")
                        print "f"

                        simu_checkOrderAndBuyWith(connectSocket, tradePrice, tradeOneHand, bullCode, file, pathTag)

                    print "g"

        # ======== update =============
        file.close()
        pathTag = []
        lastMean2 = mean2
        lastMean5 = mean5

        # time.sleep(1)
    disconnect(connectSocket)
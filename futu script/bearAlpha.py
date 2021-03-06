#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *
import datetime
import threading

# 恒指瑞银六九熊   68306   21000

# golden cross
# ==================== config =========================
oneTickTime = 1

host = "localhost"
port = 11111

targetCode = "68306"
indexCode = "800000" # 恒指
bearCode = targetCode
indexRecyclePrice = 21000
tradeOneHand = 10000

ema1Count = 60 / oneTickTime # 1分钟的tick数
ema5Count = 60 * 5 / oneTickTime #5分钟tick

ema1_K = float(2.0 / (ema1Count + 1))
ema5_K = float(2.0 / (ema5Count + 1))

windowCount = 60
# =========================================================
counter = 0

mean1 = 0
mean5 = 0

lastMean1 = 0
lastMean5 = 0

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
        elif isInMidRestTime():
            continue
        elif isTimeToExit():
            print "time to exit"
            break

        file = open("bear alpha log.txt", "a+")

        # ========== moving average ================
        currentTarget = getCurrentPrice(connectSocket, targetCode)
        print "counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')

        currentIndex = getCurrentPrice(connectSocket, indexCode)

        if flag: # one tick 触发一次
            flag = False

            mean1 = updateMeanBy(floatPrice(currentTarget), ema1_K, mean1)
            mean5 = updateMeanBy(floatPrice(currentTarget), ema5_K, mean5)

            print "mean1 ", str(mean1), " mean5 ", str(mean5)
            counter += 1

        if counter > windowCount:

            pathTag.extend(["counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"])
            pathTag.extend(["mean1 ", str(mean1), " mean5 ", str(mean5), "\n"])

            bearBuy1Price = ""
            bearSell1Price = ""
            bearGearArr = getGearData(connectSocket, bearCode, 1)
            if bearGearArr is not None:
                bearBuy1Price = bearGearArr[0]["BuyPrice"]
                bearSell1Price = bearGearArr[0]["SellPrice"]

            # ============== inquire position =====================
            positionArr = simu_inquirePosition(connectSocket)
            hasBearPosition = ifHasPositon(positionArr, bearCode)
            positionCost = getPositionPrice(positionArr, bearCode)
            positionQty = getPositionQty(positionArr, bearCode)
            positionRatio = getPositionRatio(positionArr, bearCode)

            print "hasBearPosition ", hasBearPosition

            # ============== inquire order ========================

            if hasBearPosition:
                if isInWarningTime():
                    tradePrice = bearBuy1Price
                    pathTag.append(" 4 ")
                    print "d"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bearCode, file, pathTag)

                elif floatPrice(currentTarget) - floatPrice(positionCost) > 0: #及时清仓
                    tradePrice = currentTarget
                    pathTag.append(" 8 ")
                    print "j"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bearCode, file, pathTag)

                elif lastMean1 < lastMean5 and mean1 > mean5:
                    tradePrice = currentTarget
                    pathTag.append(" 1 ")
                    print "a"

                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bearCode, file, pathTag)

                elif positionRatio < -0.03:
                    tradePrice = currentTarget
                    pathTag.append(" 3 ")
                    print "c"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bearCode, file, pathTag)

            else:
                if abs(floatPrice(currentIndex) - indexRecyclePrice) < 300:
                    print "too near recycle price"
                elif not isInGoldenTime():
                    pathTag.append(" not in golden time ")
                    print "not in golden time"
                else:

                    if lastMean1 > lastMean5 and mean1 < mean5:
                        tradePrice = currentTarget
                        pathTag.append(" 6 ")
                        print "f"
                        simu_checkOrderAndBuyWith(connectSocket, tradePrice, tradeOneHand, bearCode, file, pathTag)

                    print "g"

        # ======== update =============
        file.close()
        pathTag = []
        lastMean1 = mean1
        lastMean5 = mean5

    disconnect(connectSocket)
#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *
import datetime
import threading

# 恒指法兴七七牛   67836   20708

# golden cross
# ==================== config =========================
oneTickTime = 1

host = "localhost"
port = 11111

targetCode = "67836"
indexCode = "800000" # 恒指
bullCode = targetCode
indexRecyclePrice = 20708
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

        file = open("bull alpha log.txt", "a+")

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

                elif positionRatio < -0.02:
                    tradePrice = currentTarget
                    pathTag.append(" 3 ")
                    print "c"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bullCode, file, pathTag)

                elif floatPrice(positionCost) >= floatPrice(bullBuy1Price) and floatPrice(positionCost) <= floatPrice(bullSell1Price):
                    tradePrice = strPriceFromFloat(floatPrice(positionCost) + 0.001)
                    pathTag.append(" 8 ")
                    print "j"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bullCode, file, pathTag)

                elif floatPrice(positionCost) < floatPrice(bullBuy1Price):
                    tradePrice = currentTarget
                    pathTag.append(" 1 ")
                    print "a"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bullCode, file, pathTag)

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
                        simu_checkOrderAndBuyWith(connectSocket, tradePrice, tradeOneHand, bullCode, file, pathTag)

                    print "g"

        # ======== update =============
        file.close()
        pathTag = []
        lastMean1 = mean1
        lastMean5 = mean5

    disconnect(connectSocket)
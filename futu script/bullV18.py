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

ema10sCount = 10 / oneTickTime #10秒
ema1Count = 60 / oneTickTime # 1分钟的tick数

ema30Count = 60 * 30 / oneTickTime
ema60Count = 60 * 60 / oneTickTime

ema10s_K = float(2.0 / (ema10sCount + 1))
ema1_K = float(2.0 / (ema1Count + 1))

ema30_K = float(2.0 / (ema30Count + 1))
ema60_K = float(2.0 / (ema60Count + 1))

windowCount = 60
# =========================================================
counter = 0

mean10s = 0
mean1 = 0
mean30 = 0
mean60 = 0

lastMean10s = 0
lastMean1 = 0
lastMean30 = 0
lastMean60 = 0

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

            mean10s = updateMeanBy(floatPrice(currentTarget), ema10s_K, mean10s)
            mean1 = updateMeanBy(floatPrice(currentTarget), ema1_K, mean1)
            mean30 = updateMeanBy(floatPrice(currentTarget), ema30_K, mean30)
            mean60 = updateMeanBy(floatPrice(currentTarget), ema60_K, mean60)

            counter += 1

        if counter > windowCount:

            pathTag.extend(["counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"])

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

                elif floatPrice(bullSell1Price) < floatPrice(positionCost):#止损
                    tradePrice = bullBuy1Price
                    pathTag.append(" 444 ")
                    print "444"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bullCode, file, pathTag)

                elif floatPrice(bullSell1Price) - floatPrice(bullBuy1Price) > 0.002 and \
                        floatPrice(bullSell1Price) - floatPrice(currentTarget) > floatPrice(currentTarget) - floatPrice(bullBuy1Price):
                    pathTag.append(" fly over ")
                    print "fly over"
                    pass

                elif floatPrice(bullBuy1Price) > floatPrice(positionCost):
                    tradePrice = currentTarget
                    pathTag.append(" 3 ")
                    print "c"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bullCode, file, pathTag)

                elif floatPrice(positionCost) >= floatPrice(bullBuy1Price) and floatPrice(positionCost) <= floatPrice(bullSell1Price):
                    tradePrice = strPriceFromFloat(floatPrice(positionCost) + 0.001)
                    pathTag.append(" 8 ")
                    print "j"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bullCode, file, pathTag)

            else:
                if abs(floatPrice(currentIndex) - indexRecyclePrice) < 300:
                    print "too near recycle price"
                elif not isInGoldenTime():
                    pathTag.append(" not in golden time ")
                    print "not in golden time"
                else:
                    if mean30 > mean60:
                        if floatPrice(bullSell1Price) - floatPrice(bullBuy1Price) > 0.002 and \
                                floatPrice(bullSell1Price) - floatPrice(currentTarget) > floatPrice(currentTarget) - floatPrice(bullBuy1Price):
                            tradePrice = currentTarget
                            pathTag.append(" sss ")
                            print "sss"
                            simu_checkOrderAndBuyWith(connectSocket, tradePrice, tradeOneHand, bullCode, file, pathTag)

                        elif lastMean10s > lastMean1 and mean10s < mean1:
                            tradePrice = bullBuy1Price
                            pathTag.append(" 6 ")
                            print "f"
                            simu_checkOrderAndBuyWith(connectSocket, tradePrice, tradeOneHand, bullCode, file, pathTag)

                    print "g"

        # ======== update =============
        file.close()
        pathTag = []
        lastMean10s = mean10s
        lastMean1 = mean1
        lastMean30 = mean30
        lastMean60 = mean60

    disconnect(connectSocket)
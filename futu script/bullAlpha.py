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
oneTickTime = 1

host = "localhost"
port = 11111

targetCode = "800000" # 恒指
bullCode = "63331"
bullRecyclePrice = 19650
tradeOneHand = 10000

ema10sCount = 10 / oneTickTime #10秒
ema1Count = 60 / oneTickTime # 1分钟的tick数
ema5Count = 60 * 5 / oneTickTime #5分钟tick
windowCount = 60
# =========================================================
counter = 0

targetList = []

mean10s = 0
mean1 = 0
mean5 = 0

ema10s_K = float(2.0 / (ema10sCount + 1))
ema1_K = float(2.0 / (ema1Count + 1))
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
            print "game not begin"
            continue
        elif isTimeToExit():
            print "time to exit"
            break

        file = open("bull alpha log.txt", "a+")
        # ============== inquire position =====================
        positionArr = simu_inquirePosition(connectSocket)
        # ========== moving average ================
        currentTarget = getCurrentPrice(connectSocket, targetCode)
        print "counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')

        if flag: # one tick 触发一次
            flag = False

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

            print "mean10s ", str(mean10s), " mean1", str(mean1), " mean5 ", str(mean5)
            counter += 1

        if counter > windowCount:

            pathTag.extend(["counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"])
            pathTag.extend(["mean10s ", str(mean10s), " mean1", str(mean1), " mean5 ", str(mean5), "\n"])

            bullBuy1Price = ""
            bullSell1Price = ""
            bullGearArr = getGearData(connectSocket, bullCode, 1)
            if bullGearArr is not None:
                bullBuy1Price = bullGearArr[0]["BuyPrice"]
                bullSell1Price = bullGearArr[0]["SellPrice"]

            hasBullPosition = ifHasPositon(positionArr, tradeOneHand, bullCode)
            positionCost = getPositionPrice(positionArr, bullCode)
            if hasBullPosition:
                if floatPrice(bullBuy1Price) > floatPrice(positionCost):
                    tradePrice = bullBuy1Price
                    pathTag.append(" 1 ")
                    print "a"
                elif floatPrice(bullBuy1Price) <= floatPrice(positionCost) and floatPrice(bullSell1Price) >= floatPrice(positionCost):
                    tradePrice = strPriceFromFloat(floatPrice(positionCost) + 0.001)
                    pathTag.append(" 2 ")
                    print "b"
                else:
                    tradePrice = bullBuy1Price
                    pathTag.append(" 3 ")
                    print "c"

                if isInWarningTime():
                    tradePrice = bullBuy1Price
                    pathTag.append(" 4 ")
                    print "d"

                simu_checkOrderAndSellWith(connectSocket, tradePrice, tradeOneHand, bullCode, file, pathTag)

            else:
                if abs(floatPrice(currentTarget) - bullRecyclePrice) < 300:
                    print "too near recycle price"
                elif not isInGoldenTime():
                    pathTag.append(" not in golden time ")
                    print "not in golden time"
                elif mean1 < mean5 and mean10s > mean1:
                    if (mean10s - mean1) > 8:
                        tradePrice = bullSell1Price
                        pathTag.append(" 5 ")
                        print "e"
                    else:
                        tradePrice = bullBuy1Price
                        pathTag.append(" 6 ")
                        print "f"

                    simu_checkOrderAndBuyWith(connectSocket, tradePrice, tradeOneHand, bullCode, file, pathTag)


        # ======== update =============
        file.close()
        pathTag = []

        # time.sleep(0.1)
    disconnect(connectSocket)
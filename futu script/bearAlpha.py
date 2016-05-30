#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *
import datetime
import threading

# 恒指法巴七二熊   66503   21000

# golden cross
# ==================== config =========================
oneTickTime = 1

host = "localhost"
port = 11111

targetCode = "800000" # 恒指
bearCode = "66503"
bearRecyclePrice = 21000
tradeOneHand = 10000

ema10sCount = 10 / oneTickTime #10秒
ema5Count = 60 * 5 / oneTickTime #5分钟tick

ema10s_K = float(2.0 / (ema10sCount + 1))
ema5_K = float(2.0 / (ema5Count + 1))

windowCount = 60
# =========================================================
counter = 0

mean10s = 0
mean5 = 0

lastMean10s = 0
lastMean5 = 0

pathTag = []

flag = False

# ================ trigger ========================
def trigger():
    global flag
    while True:
        if isInMidRestTime():
            continue
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

        file = open("bear alpha log.txt", "a+")

        # ========== moving average ================
        currentTarget = getCurrentPrice(connectSocket, targetCode)
        print "counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')

        if flag: # one tick 触发一次
            flag = False

            mean10s = updateMeanBy(floatPrice(currentTarget), ema10s_K, mean10s)
            mean5 = updateMeanBy(floatPrice(currentTarget), ema5_K, mean5)

            print "mean10s", str(mean10s), " mean5 ", str(mean5)
            counter += 1

        if counter > windowCount:

            pathTag.extend(["counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"])
            pathTag.extend(["mean10s", str(mean10s), " mean5 ", str(mean5), "\n"])

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

                elif lastMean10s < lastMean5 and mean10s > mean5:
                    tradePrice = bearBuy1Price
                    pathTag.append(" 1 ")
                    print "a"

                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bearCode, file, pathTag)

                elif positionRatio < -0.03:
                    tradePrice = bearBuy1Price
                    pathTag.append(" 3 ")
                    print "c"
                    simu_checkOrderAndSellWith(connectSocket, tradePrice, positionQty, bearCode, file, pathTag)

            else:
                if abs(floatPrice(currentTarget) - bearRecyclePrice) < 300:
                    print "too near recycle price"
                elif not isInGoldenTime():
                    pathTag.append(" not in golden time ")
                    print "not in golden time"
                else:
                    if lastMean10s > lastMean5 and mean10s < mean5:
                        tradePrice = bearSell1Price
                        pathTag.append(" 6 ")
                        print "f"

                        simu_checkOrderAndBuyWith(connectSocket, tradePrice, tradeOneHand, bearCode, file, pathTag)

                    print "g"

        # ======== update =============
        file.close()
        pathTag = []
        lastMean10s = mean10s
        lastMean5 = mean5

    disconnect(connectSocket)
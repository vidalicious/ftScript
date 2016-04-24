#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *

# 恒指瑞银七六牛K.C    65319   10000
# 恒指瑞银六七熊T.P    65281   10000

# price = k * target + b
# ================ config =================
oneTickTime = 1

host = "localhost"
port = 11111

targetCode = "800000" # 恒指
bullCode = "65319"
bearCode = "65281"
tradeOneHand = 10000

emaCount = 60 / oneTickTime
windowCount = 60

# ============================================
counter = 0

meanTarget = 0
meanBull = 0

ema_K = float(2 / (emaCount + 1))

meanTargetList = []
meanBullList = []

bullTrend_buySignal = False
bullTrend_sellSignal = False
bullGear_buySignal = False
bullGear_sellSignal = False
bullBuySignal = False
bullSellSignal = False

pathTag = []

# ===========================================================
connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        file = open("bullAndBearLog", "a+")

        # ============== inquire position =====================
        positionArr = simu_inquirePosition(connectSocket)

        # ============== mapping ========================
        currentTarget = getCurrentPrice(connectSocket, targetCode)
        print "counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')

        if meanTarget != 0:
            meanTarget = floatPrice(currentTarget) * ema_K + meanTarget * (1 - ema_K)
        else:
            meanTarget = floatPrice(currentTarget)

        meanTargetList.insert(0, meanTarget)
        if len(meanTargetList) > windowCount:
            meanTargetList = meanTargetList[:windowCount]

        currentBullPrice = getCurrentPrice(connectSocket, bullCode)
        print "bull ", str(floatPrice(currentBullPrice))

        if meanBull != 0:
            meanBull = floatPrice(currentBullPrice) * ema_K + meanBull * (1 - ema_K)
        else:
            meanBull = floatPrice(currentBullPrice)

        meanBullList.insert(0, meanBull)
        if len(meanBullList) > windowCount:
            meanBullList = meanBullList[:windowCount]

        if counter > emaCount:
            x1 = meanTarget
            y1 = meanBull
            x2 = meanTargetList[-1]
            y2 = meanBullList[-1]

            para_k = 0
            para_b = 0
            if x1 != x2:
                para_k = (y1 - y2) / (x1 - x2)
                para_b = ((x1 * y2) - (x2 * y1)) / (x1 - x2)
            else:
                para_k = y1 / x1
                para_b = 0

            numericalBullPrice = floatPrice(currentTarget) * para_k + para_b

            if floatPrice(currentBullPrice) < numericalBullPrice:
                bullTrend_buySignal = True
                pathTag.append(" 1 ")
            elif floatPrice(currentBullPrice) > numericalBullPrice:
                bullTrend_sellSignal = True
                pathTag.append(" 2 ")

            bullGearArr = getGearData(connectSocket, bullCode, 1)
            if bullGearArr is not None:
                bullBuy1Price = floatPrice(bullGearArr[0]["BuyPrice"])
                bullBuy1Vol = float(bullGearArr[0]["BuyVol"])
                bullSell1Price = floatPrice(bullGearArr[0]["SellPrice"])
                bullSell1Vol = float(bullGearArr[0]["SellVol"])

                if bullBuy1Vol / bullSell1Vol > 15:
                    bullGear_buySignal = True
                    pathTag.append(" 3 ")
                elif bullSell1Vol / bullBuy1Vol > 15:
                    bullGear_sellSignal = True
                    pathTag.append(" 4 ")

            hasBullPosition = ifHasPositon(positionArr, tradeOneHand, bullCode)
            bullPositionRatio = getPositionRatio(positionArr, bullCode)

            if bullTrend_buySignal and bullGear_buySignal:
                bullBuySignal = True
                pathTag.append(" 5 ")
            if bullTrend_sellSignal:
                bullSellSignal = True
                pathTag.append(" 6 ")
            if bullPositionRatio < -0.03:  # 止损
                bullSellSignal = True
                pathTag.append(" 7 ")

            if bullBuySignal:
                if not hasBullPosition:
                    hasBuyOrder = False
                    orderInfoArr = simu_inquireOrder(connectSocket)
                    currentBullPrice = getCurrentPrice(connectSocket, bullCode)
                    if orderInfoArr is not None:
                        for orderInfo in orderInfoArr:
                            if orderInfo["StockCode"] == bullCode and orderInfo["Status"] == "1":
                                if orderInfo["OrderSide"] == "0" and orderInfo["Price"] == currentBullPrice:
                                    hasBuyOrder = True
                                else:
                                    simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)  # 撤单
                                    pathTag.append(" 撤单 ")

                    if not hasBuyOrder:  # 如果没有未成交合适订单则下单
                        localID = simu_commonBuyOrder(connectSocket, currentBullPrice, tradeOneHand, bullCode)
                        print "buy bull", bullCode, " at ", floatPrice(currentBullPrice), "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID
                        logger = ["buy bull", bullCode, " at ", str(floatPrice(currentBullPrice)), "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID, "\n"]
                        file.writelines(logger)
                        pathTag.append("\n")
                        file.writelines(pathTag)

            elif bullSellSignal:
                if hasBullPosition:
                    hasSellOrder = False
                    orderInfoArr = simu_inquireOrder(connectSocket)
                    currentBullPrice = getCurrentPrice(connectSocket, bullCode)
                    if orderInfoArr is not None:
                        for orderInfo in orderInfoArr:
                            if orderInfo["StockCode"] == bullCode and orderInfo["Status"] == "1":
                                if orderInfo["OrderSide"] == "1" and orderInfo["Price"] == currentBullPrice:
                                    hasSellOrder = True
                                else:
                                    simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)  # 撤单
                                    pathTag.append(" 撤单 ")

                    if not hasSellOrder:
                        localID = simu_commonSellOrder(connectSocket, currentBullPrice, tradeOneHand, bullCode)
                        print "sell bull ", bullCode, " at ", floatPrice(currentBullPrice), "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID
                        logger = ["sell bull ", bullCode, " at ", str(floatPrice(currentBullPrice)), "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID, "\n"]
                        file.writelines(logger)
                        pathTag.append("\n")
                        file.writelines(pathTag)

        # ======== update ==============
        file.close()
        counter += 1

        bullTrend_buySignal = False
        bullTrend_sellSignal = False
        bullGear_buySignal = False
        bullGear_sellSignal = False
        bullBuySignal = False
        bullSellSignal = False
        pathTag = []

        time.sleep(oneTickTime)
    disconnect(connectSocket)
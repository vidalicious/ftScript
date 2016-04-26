#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *
import datetime

# 恒指瑞银七六牛K.C    65319   10000
# 恒指瑞银六七熊T.P    65281   10000

# improved macd
# ==================== config =========================
oneTickTime = 1

host = "localhost"
port = 11111

targetCode = "800000" # 恒指
bullCode = "65319"
tradeOneHand = 10000

ema1Count = 60 / oneTickTime # 1分钟的tick数
ema5Count = 60 * 5 / oneTickTime #5分钟tick
windowCount = 60
# =========================================================
counter = 0

targetList = []

mean1 = 0
mean5 = 0

# 方差
variance1 = 0
# 标准差
standardDeviation1 = 0

ema1_K = float(2.0 / (ema1Count + 1))
ema5_K = float(2.0 / (ema5Count + 1))

bullTrend_buySignal = False
bullTrend_sellSignal = False
bullGear_buySignal = False
bullGear_sellSignal = False
bullBuySignal = False
bullSellSignal = False

pathTag = []

# ==========================================================
connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        file = open("bullAndBearLog", "a+")
        # ============== inquire position =====================
        positionArr = simu_inquirePosition(connectSocket)
        # ========== moving average ================
        currentTarget = getCurrentPrice(connectSocket, targetCode)
        print "counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')

        targetList.insert(0, floatPrice(currentTarget))
        if len(targetList) > windowCount:
            targetList = targetList[:windowCount]

        if mean1 != 0:
            mean1 = floatPrice(currentTarget) * ema1_K + mean1 * (1 - ema1_K)
        else:
            mean1 = floatPrice(currentTarget)

        if mean5 != 0:
            mean5 = floatPrice(currentTarget) * ema5_K + mean5 * (1 - ema5_K)
        else:
            mean5 = floatPrice(currentTarget)

        variance1 = getVarianceFromList(targetList, mean1)
        standardDeviation1 = sqrt(variance1)

        print "mean1", str(mean1), " mean5 ", str(mean5)

        if counter > windowCount:
            if mean1 > mean5:
                bullTrend_buySignal = True
                pathTag.append(" 1 ")
                print "a"
            elif mean1 < mean5:
                bullTrend_sellSignal = True
                pathTag.append(" 2 ")
                print "b"

            bullBuy1Price = ""
            bullSell1Price = ""
            bullGearArr = getGearData(connectSocket, bullCode, 1)
            if bullGearArr is not None:
                bullBuy1Price = bullGearArr[0]["BuyPrice"]
                bullSell1Price = bullGearArr[0]["SellPrice"]

            hasBullPosition = ifHasPositon(positionArr, tradeOneHand, bullCode)
            bullPositionRatio = getPositionRatio(positionArr, bullCode)

            if standardDeviation1 < 10: # 方差太小，离场
                bullSellSignal = True
                pathTag.append(" small standard deviation ")
                print "small standard deviation"
            elif datetime.datetime.now().time() > datetime.time(15, 58, 0): # 倒数2分钟，离场
                bullSellSignal = True
                pathTag.append(" too late ")
                print "too late"
            else:
                if bullTrend_buySignal:
                    bullBuySignal = True
                    pathTag.append(" 7 ")
                    print "c"
                if bullTrend_sellSignal:
                    bullSellSignal = True
                    pathTag.append(" 8 ")
                    print "d"
                if hasBullPosition and bullPositionRatio < -0.03: #止损
                    bullSellSignal = True
                    pathTag.append(" 9 ")
                    print "e"

            if bullBuySignal:
                if not hasBullPosition:
                    hasBuyOrder = False
                    orderInfoArr = simu_inquireOrder(connectSocket)
                    tradePrice = bullSell1Price #卖1价
                    if orderInfoArr is not None:
                        for orderInfo in orderInfoArr:
                            if orderInfo["StockCode"] == bullCode and orderInfo["Status"] == "1":
                                if orderInfo["OrderSide"] == "0" and orderInfo["Price"] == tradePrice:
                                    hasBuyOrder = True
                                else:
                                    simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)  # 撤单
                                    pathTag.append(" 撤单 ")

                    if not hasBuyOrder:  # 如果没有未成交合适订单则下单
                        localID = simu_commonBuyOrder(connectSocket, tradePrice, tradeOneHand, bullCode)
                        print "buy bull ", bullCode, " at ", floatPrice(tradePrice), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID
                        logger = ["buy bull ", bullCode, " at ", str(floatPrice(tradePrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, "\n"]
                        file.writelines(logger)
                        pathTag.append("\n")
                        file.writelines(pathTag)

            elif bullSellSignal:
                if hasBullPosition:
                    hasSellOrder = False
                    orderInfoArr = simu_inquireOrder(connectSocket)
                    tradePrice = bullBuy1Price
                    if orderInfoArr is not None:
                        for orderInfo in orderInfoArr:
                            if orderInfo["StockCode"] == bullCode and orderInfo["Status"] == "1":
                                if orderInfo["OrderSide"] == "1" and orderInfo["Price"] == tradePrice:
                                    hasSellOrder = True
                                else:
                                    simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)  # 撤单
                                    pathTag.append(" 撤单 ")

                    if not hasSellOrder:
                        localID = simu_commonSellOrder(connectSocket, tradePrice, tradeOneHand, bullCode)
                        print "sell bull ", bullCode, " at ", floatPrice(tradePrice), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID
                        logger = ["sell bull ", bullCode, " at ", str(floatPrice(tradePrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, "\n"]
                        file.writelines(logger)
                        pathTag.append("\n")
                        file.writelines(pathTag)

        # ======== update =============
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
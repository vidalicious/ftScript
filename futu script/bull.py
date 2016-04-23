#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *

# 恒指瑞银七六牛K.C    65319   10000
# 恒指瑞银六七熊T.P    65281   10000

# ==================== config =========================
oneTickTime = 1
bollingerRadius = 2 # 2倍标准差

host = "localhost"
port = 11111

targetCode = "800000" # 恒指
bullCode = "65319"
bearCode = "65281"
tradeOneHand = 10000

movingAverageCount = 60 / oneTickTime # 1分钟的tick数

# =================================================================
counter = 0

targetList = []

# 均值
mean = 0
# 方差
variance = 0
# 标准差
standardDeviation = 0

meanList = []

lastTarget = 0

class MARelation:
    DEFAULT = 0
    BELOW = 1
    ABOVE = 2

currentRelation = MARelation.DEFAULT
lastRelation = MARelation.DEFAULT

bullTrend_buySignal = False
bullTrend_sellSignal = False
bullGear_buySignal = False
bullGear_sellSignal = False
bullBuySignal = False
bullSellSignal = False


# =================================================================
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
        if len(targetList) > movingAverageCount:
            targetList = targetList[:movingAverageCount]

        mean = getMeanFromList(targetList)
        meanList.insert(0, mean)
        if len(meanList) > movingAverageCount:
            meanList = meanList[:movingAverageCount]
        variance = getVarianceFromList(targetList, mean)
        standardDeviation = sqrt(variance)

        if floatPrice(currentTarget) < mean:
            currentRelation = MARelation.BELOW
        else:
            currentRelation = MARelation.ABOVE

        # ============== bull ===========================
        if counter > 10:
            if meanList[0] > meanList[-1]: #上升趋势
                if lastRelation == MARelation.BELOW and currentRelation == MARelation.ABOVE:
                    bullTrend_buySignal = True
                if floatPrice(currentTarget) > mean + standardDeviation * bollingerRadius:
                    bullTrend_sellSignal = True
            elif meanList[0] < meanList[-1]: #下降趋势
                if lastRelation == MARelation.ABOVE and currentRelation == MARelation.BELOW:
                    bullTrend_sellSignal = True
                if floatPrice(currentTarget) < mean - standardDeviation * bollingerRadius:
                    bullTrend_buySignal = True
            else: #不动趋势
                bullTrend_sellSignal = True

            bullGearArr = getGearData(connectSocket, bullCode, 1)
            if bullGearArr is not None:
                bullBuy1Price = floatPrice(bullGearArr[0]["BuyPrice"])
                bullBuy1Vol = float(bullGearArr[0]["BuyVol"])
                bullSell1Price = floatPrice(bullGearArr[0]["SellPrice"])
                bullSell1Vol = float(bullGearArr[0]["SellVol"])

                if bullBuy1Vol / bullSell1Vol > 15:
                    bullGear_buySignal = True
                elif bullSell1Vol / bullBuy1Vol > 15:
                    bullGear_sellSignal = True

            hasBullPosition = ifHasPositon(positionArr, tradeOneHand, bullCode)
            bullPositionRatio = getPositionRatio(positionArr, bullCode)

            if bullTrend_buySignal and bullGear_buySignal:
                bullBuySignal = True
            if bullTrend_sellSignal:
                bullSellSignal = True
            if bullPositionRatio < -0.03: #止损
                bullSellSignal = True

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

                    if not hasBuyOrder:  # 如果没有未成交合适订单则下单
                        localID = simu_commonBuyOrder(connectSocket, currentBullPrice, tradeOneHand, bullCode)
                        print "buy bull", bullCode, " at ", floatPrice(currentBullPrice), "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID
                        logger = ["buy bull", bullCode, " at ", floatPrice(currentBullPrice), "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID, "\n"]
                        file.writelines(logger)

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

                    if not hasSellOrder:
                        localID = simu_commonSellOrder(connectSocket, currentBullPrice, tradeOneHand, bullCode)
                        print "sell bull ", bullCode, " at ", floatPrice(currentBullPrice), "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID
                        logger = ["sell bull ", bullCode, " at ", floatPrice(currentBullPrice), "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID, "\n"]
                        file.writelines(logger)

        # ========== update ===============
        file.close()
        counter += 1
        lastTarget = currentTarget
        lastRelation = currentRelation

        bullTrend_buySignal = False
        bullTrend_sellSignal = False
        bullGear_buySignal = False
        bullGear_sellSignal = False
        bullBuySignal = False
        bullSellSignal = False

        time.sleep(oneTickTime)
    disconnect(connectSocket)




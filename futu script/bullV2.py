#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *

# 恒指瑞银七六牛K.C    65319   10000
# 恒指瑞银六七熊T.P    65281   10000

# macd
# ==================== config =========================
oneTickTime = 1

host = "localhost"
port = 11111

targetCode = "800000" # 恒指
bullCode = "65319"
bearCode = "65281"
tradeOneHand = 10000

ema1Count = 60 / oneTickTime # 1分钟的tick数
ema5Count = 60 * 5 / oneTickTime #5分钟tick
windowCount = 60
# =========================================================
counter = 0

targetList = []

mean1 = 0
mean5 = 0

ema1_K = float(2 / (ema1Count + 1))
ema5_K = float(2 / (ema5Count + 1))

mean1List = []
mean5List = []

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
        mean1List.insert(0, mean1)
        if len(mean1List) > windowCount:
            mean1List = mean1List[:windowCount]

        if mean5 != 0:
            mean5 = floatPrice(currentTarget) * ema5_K + mean5 * (1 - ema5_K)
        else:
            mean5 = floatPrice(currentTarget)
        mean5List.insert(0, mean5)
        if len(mean5List) > windowCount:
            mean5List = mean5List[:windowCount]

        print "mean1 ", str(mean1), " mean5 ", str(mean5)

        if counter > ema1Count:
            if mean1 < mean5:
                if mean1 > mean1List[1]: #ema1斜率向上
                    bullTrend_buySignal = True
                    pathTag.append(" 1 ")
                    print "a"
            else:
                if mean1 < mean1List[1]: #斜率向下
                    bullTrend_sellSignal = True
                    pathTag.append(" 2 ")
                    print "b"

            if mean1 > mean5 and mean1List[1] < mean5List[1]: #ema1 向上穿越ema5
                bullTrend_buySignal = True
                pathTag.append(" 3 ")
                print "c"

            if mean1 < mean5 and mean1List[1] > mean5List[1]: #向下穿越
                bullTrend_sellSignal = True
                pathTag.append(" 4 ")
                print "d"

            # bullGearArr = getGearData(connectSocket, bullCode, 1)
            # if bullGearArr is not None:
            #     bullBuy1Price = floatPrice(bullGearArr[0]["BuyPrice"])
            #     bullBuy1Vol = float(bullGearArr[0]["BuyVol"])
            #     bullSell1Price = floatPrice(bullGearArr[0]["SellPrice"])
            #     bullSell1Vol = float(bullGearArr[0]["SellVol"])
            #
            #     if bullBuy1Vol / bullSell1Vol > 15:
            #         bullGear_buySignal = True
            #         pathTag.append(" 5 ")
            #     elif bullSell1Vol / bullBuy1Vol > 15:
            #         bullGear_sellSignal = True
            #         pathTag.append(" 6 ")

            hasBullPosition = ifHasPositon(positionArr, tradeOneHand, bullCode)
            bullPositionRatio = getPositionRatio(positionArr, bullCode)

            if bullTrend_buySignal:
                bullBuySignal = True
                pathTag.append(" 7 ")
            if bullTrend_sellSignal:
                bullSellSignal = True
                pathTag.append(" 8 ")
            if hasBullPosition and bullPositionRatio < -0.03: #止损
                bullSellSignal = True
                pathTag.append(" 9 ")

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
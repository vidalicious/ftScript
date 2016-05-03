#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *
import datetime
import threading

# 恒指摩通六八熊   66248   21305

# improved macd + thread
# ==================== config =========================
oneTickTime = 1

host = "localhost"
port = 11111

targetCode = "800000" # 恒指
bearCode = "66248"
bearRecyclePrice = 21305
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
variance5 = 0
# 标准差
standardDeviation5 = 0

ema1_K = float(2.0 / (ema1Count + 1))
ema5_K = float(2.0 / (ema5Count + 1))

bearTrend_buySignal = False
bearTrend_sellSignal = False
bearBuySignal = False
bearSellSignal = False

moreThanLargeSDTag = False # > large

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
        file = open("bear alpha log", "a+")
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

            if mean1 != 0:
                mean1 = floatPrice(currentTarget) * ema1_K + mean1 * (1 - ema1_K)
            else:
                mean1 = floatPrice(currentTarget)

            if mean5 != 0:
                mean5 = floatPrice(currentTarget) * ema5_K + mean5 * (1 - ema5_K)
            else:
                mean5 = floatPrice(currentTarget)

            variance5 = getVarianceFromList(targetList, mean5)
            standardDeviation5 = sqrt(variance5)

            print "mean1", str(mean1), " mean5 ", str(mean5)
            counter += 1

        if counter > windowCount:
            if mean1 < mean5:
                bearTrend_buySignal = True
                pathTag.append(" 1 ")
                print "a"
            elif mean1 > mean5:
                bearTrend_sellSignal = True
                pathTag.append(" 2 ")
                print "b"

            bearBuy1Price = ""
            bearSell1Price = ""
            bearGearArr = getGearData(connectSocket, bearCode, 1)
            if bearGearArr is not None:
                bearBuy1Price = bearGearArr[0]["BuyPrice"]
                bearSell1Price = bearGearArr[0]["SellPrice"]

            hasBearPosition = ifHasPositon(positionArr, tradeOneHand, bearCode)
            bearPositionRatio = getPositionRatio(positionArr, bearCode)

            if abs(floatPrice(currentTarget) - bearRecyclePrice) < 300:
                bearSellSignal = True
                pathTag.append(" too near recycle price ")
                print "too near recycle price"
            elif standardDeviation5 < 8: # 方差太小，离场
                bearSellSignal = True
                pathTag.append(" small standard deviation ")
                print "small standard deviation"
            elif datetime.datetime.now().time() > datetime.time(15, 58, 0): # 倒数2分钟，离场
                bearSellSignal = True
                pathTag.append(" too late ")
                print "too late"
            else:
                if bearTrend_buySignal:
                    bearBuySignal = True
                    pathTag.append(" 7 ")
                    print "c"
                if bearTrend_sellSignal:
                    bearSellSignal = True
                    pathTag.append(" 8 ")
                    print "d"
                if hasBearPosition and bearPositionRatio < -0.03: #止损
                    bearSellSignal = True
                    pathTag.append(" 9 ")
                    print "e"

            if standardDeviation5 > 20:
                moreThanLargeSDTag = True
                pathTag.append(" large sd tag ")
                print "large sd tag"

            if bearBuySignal:
                if not hasBearPosition:
                    hasBuyOrder = False
                    orderInfoArr = simu_inquireOrder(connectSocket)
                    tradePrice = ""
                    if moreThanLargeSDTag: # 小标准差跟现价,否则跟买卖盘
                        tradePrice = bearSell1Price
                    else:
                        tradePrice = getCurrentPrice(connectSocket, bearCode)
                    if orderInfoArr is not None:
                        for orderInfo in orderInfoArr:
                            if orderInfo["StockCode"] == bearCode and (orderInfo["Status"] == "0" or orderInfo["Status"] == "1"):
                                if orderInfo["OrderSide"] == "0":
                                    hasBuyOrder = True
                                    if orderInfo["Price"] == tradePrice:
                                        pass
                                    else:
                                        # 价格不对修改订单
                                        simu_modifyOrder(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], tradePrice, tradeOneHand)
                                else:
                                    simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)  # 撤单
                                    pathTag.append(" 撤卖单 ")

                    if not hasBuyOrder:  # 如果没有未成交合适订单则下单
                        localID = simu_commonBuyOrder(connectSocket, tradePrice, tradeOneHand, bearCode)
                        print "buy bear ", bearCode, " at ", floatPrice(tradePrice), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID
                        logger = ["buy bear ", bearCode, " at ", str(floatPrice(tradePrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, "\n"]
                        file.writelines(logger)
                        pathTag.append("\n")
                        file.writelines(pathTag)

            elif bearSellSignal:
                if hasBearPosition:
                    hasSellOrder = False
                    orderInfoArr = simu_inquireOrder(connectSocket)
                    tradePrice = ""
                    if moreThanLargeSDTag: # 小标准差跟现价,否则跟买卖盘
                        tradePrice = bearBuy1Price
                    else:
                        tradePrice = getCurrentPrice(connectSocket, bearCode)
                    if orderInfoArr is not None:
                        for orderInfo in orderInfoArr:
                            if orderInfo["StockCode"] == bearCode and (orderInfo["Status"] == "0" or orderInfo["Status"] == "1"):
                                if orderInfo["OrderSide"] == "1":
                                    hasSellOrder = True
                                    if orderInfo["Price"] == tradePrice:
                                        pass
                                    else:
                                        # 价格不对修改订单
                                        simu_modifyOrder(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], tradePrice, tradeOneHand)
                                else:
                                    simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)  # 撤单
                                    pathTag.append(" 撤买单 ")

                    if not hasSellOrder:
                        localID = simu_commonSellOrder(connectSocket, tradePrice, tradeOneHand, bearCode)
                        print "sell bear ", bearCode, " at ", floatPrice(tradePrice), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID
                        logger = ["sell bear ", bearCode, " at ", str(floatPrice(tradePrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, "\n"]
                        file.writelines(logger)
                        pathTag.append("\n")
                        file.writelines(pathTag)

        # ======== update =============
        file.close()

        bearTrend_buySignal = False
        bearTrend_sellSignal = False
        bearBuySignal = False
        bearSellSignal = False
        moreThanLargeSDTag = False
        pathTag = []

        # time.sleep(0.1)
    disconnect(connectSocket)
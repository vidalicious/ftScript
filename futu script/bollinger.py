#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *

# 亚基帮租赁 01496 4000

# ====================== config =================
oneTickTime = 1
bollingRadius = 2 # 2倍标准差

host = "localhost"
port = 11111
stockCode = "01496"
tradeOneHand = 4000

shortMovingTicks = 5
longMovingTicks = 20
# ===================================================
counter = 0

# 均值
mean = 0
# 方差
variance = 0
# 标准差
standardDeviation = 0

orderID = 0
lastPrice = 0

shortTickList = [] # 原始数据
longTickList = []

shortMAList = [] # 平均后数据
longMAList = []

class MARelation:
    DEFAULT = 0
    BELOW = 1
    ABOVE = 2

class Trend:
    DEFAULT = 0
    UP = 1
    DOWN = 2
# =======================================================================


buyInSignal = False
sellOutSignal = False
lastLocalMAStatus = MARelation.DEFAULT
currentLocalMAStatus = MARelation.DEFAULT
longMATrend = Trend.DEFAULT

connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        currentPrice = getCurrentPrice(connectSocket, stockCode)
        print "currentPrice", floatPrice(currentPrice), "counter", counter, "time", time.strftime('%Y-%m-%d %H:%M:%S')

        # ============= moving average ================

        shortTickList.insert(0, floatPrice(currentPrice))
        if len(shortTickList) > shortMovingTicks:
            shortTickList = shortTickList[:shortMovingTicks]

        longTickList.insert(0, floatPrice(currentPrice))
        if len(longTickList) > longMovingTicks:
            longTickList = longTickList[:longMovingTicks]

        shortMAList.insert(0, getAveragePriceFromList(shortTickList))
        if len(shortMAList) > 5:
            shortMAList = shortMAList[:5]

        longMAList.insert(0, getAveragePriceFromList(longTickList))
        if len(longMAList) > 5:
            longMAList = longMAList[:5]

        if shortMAList[0] < longMAList[0]:
            currentLocalMAStatus = MARelation.BELOW
        else:
            currentLocalMAStatus = MARelation.ABOVE

        if counter > 50:
            if longMAList[-1] < longMAList[0]:
                longMATrend = Trend.UP
            elif longMAList[-1] > longMAList[0]:
                longMATrend = Trend.DOWN
            else:
                longMATrend = Trend.DEFAULT

        # ============== bollinger =================
        mean = (mean * counter + floatPrice(currentPrice)) / (counter + 1)
        variance = (variance * counter + (floatPrice(currentPrice) - mean) ** 2) / (counter + 1)
        standardDeviation = sqrt(variance)

        # ============== inquire position =====================
        positionArr = simu_inquirePosition(connectSocket)
        hasFullPosition = ifHasPositon(positionArr, tradeOneHand, stockCode)
        positionPrice = floatPrice(getPositionPrice(positionArr, stockCode))

        # ============== strategy ======================
        # 趋势上扬并且短期向上穿越
        if lastLocalMAStatus == MARelation.BELOW and currentLocalMAStatus == MARelation.ABOVE and longMATrend == Trend.UP:
            buyInSignal = True
        else:
            buyInSignal = False

        if lastLocalMAStatus == MARelation.ABOVE and currentLocalMAStatus == MARelation.BELOW and longMATrend == Trend.DOWN:
            sellOutSignal = True
        else:
            sellOutSignal = False

        # 止损
        if positionPrice > 0:
            if (floatPrice(currentPrice) - positionPrice) / positionPrice < -0.03:
                sellOutSignal = True
            else:
                sellOutSignal = False
        else:
            sellOutSignal = False

        if floatPrice(currentPrice) > mean + bollingRadius * standardDeviation: #顶端
            pass
        elif floatPrice(currentPrice) > mean - bollingRadius * standardDeviation\
                and floatPrice(currentPrice) <= mean + bollingRadius * standardDeviation: # 带中
            pass
        else: #底部
            pass

        if buyInSignal:
            if not hasFullPosition:
                sell_one = getSellPrice(connectSocket, stockCode, 1, 0)
                hasBuyOrder = False
                orderInfoArr = simu_inquireOrder(connectSocket)
                if orderInfoArr is not None:
                    for orderInfo in orderInfoArr:
                        if orderInfo["StockCode"] == stockCode and orderInfo["Status"] == "1":
                            if orderInfo["OrderSide"] == "0" and orderInfo["Price"] == sell_one:
                                hasBuyOrder = True
                            else:
                                simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)#撤单

                if not hasBuyOrder:#如果没有未成交合适订单则下单
                    localID = simu_commonBuyOrder(connectSocket, sell_one, tradeOneHand, stockCode)
                    orderID += 1
                    print "buy at", float(sell_one) / 1000, "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID, "orderID", orderID
                    log = ["buy at ", str(float(sell_one) / 1000), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, " orderID ", str(orderID), "\n"]
                    file = open("run log", "a+")
                    file.writelines(log)
                    file.close()

        elif sellOutSignal:
            if hasFullPosition:
                buy_one = getBuyPrice(connectSocket, stockCode, 1, 0)
                hasSellOrder = False
                orderInfoArr = simu_inquireOrder(connectSocket)
                if orderInfoArr is not None:
                    for orderInfo in orderInfoArr:
                        if orderInfo["StockCode"] == stockCode and orderInfo["Status"] == "1":
                            if orderInfo["OrderSide"] == "1" and orderInfo["Price"] == buy_one:
                                hasSellOrder = True
                            else:
                                simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)#撤单

                if not hasSellOrder:
                    localID = simu_commonSellOrder(connectSocket, buy_one, tradeOneHand, stockCode)
                    orderID += 1
                    print "sell at", float(buy_one) / 1000, "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID, "orderID", orderID
                    log = ["sell at ", str(float(buy_one) / 1000), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, " orderID ", str(orderID), "\n"]
                    file = open("run log", "a+")
                    file.writelines(log)
                    file.close()

        # 更新需要记录的参数
        lastPrice = currentPrice
        counter += 1
        lastLocalMAStatus = currentLocalMAStatus
        time.sleep(oneTickTime)
disconnect(connectSocket)

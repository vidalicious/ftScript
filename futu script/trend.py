#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
from FSApi import *
from math import *

# 亚基帮租赁 01496   4000

# 智美体育 01661     1000
# 金蝶国际 00268     2000
# 光启科学 00439     1000
# 恒大地产 03333    1000
# 永义实业  00616   5000

# 新昌管理集团 02340 4000
# 金嗓子 06896 500
# 中联重科 01157 200
# 凯升控股 00102 2000
# 南旋控股  01982   2000
# 宏安地产  01243   4000

# 恒指瑞信六九熊B.P 64940   10000
# 恒指法兴六甲牛Z.C 65205   10000

# ====================== config =================
oneTickTime = 1
bollingRadius = 2 # 2倍标准差

host = "localhost"
port = 11111
stockCode = "01157"
tradeOneHand = 200

shortMovingTicks = 10
longMovingTicks = 50
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

lastBuyOnePrice = 0
lastSellOnePrice = 0
lastBuyOneVol = 0
lastSellOneVol = 0

currentBuyOnePrice = 0
currentSellOnePrice = 0
currentBuyOneVol = 0
currentSellOneVol = 0

lastMidGearPrice = 0
currentMidGearPrice = 0
gearStableCounter = 0

# =======================================================================

MABuyInSignal = False
MASellOutSignal = False

gearBuyInSignal = False
gearSellOutSignal = False

buyInSignal = False
sellOutSignal = False
lastLocalMAStatus = MARelation.DEFAULT
currentLocalMAStatus = MARelation.DEFAULT
longMATrend = Trend.DEFAULT
shortMATrend = Trend.DEFAULT

connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        currentPrice = getCurrentPrice(connectSocket, stockCode)
        print "currentPrice", floatPrice(currentPrice), "counter", counter, "time", time.strftime('%Y-%m-%d %H:%M:%S')

        # ============== inquire position =====================
        positionArr = simu_inquirePosition(connectSocket)
        hasFullPosition = ifHasPositon(positionArr, tradeOneHand, stockCode)
        positionRatio = getPositionRatio(positionArr, stockCode)
        print "tag 1"

        # ============= moving average ================

        shortTickList.insert(0, floatPrice(currentPrice))
        if len(shortTickList) > shortMovingTicks:
            shortTickList = shortTickList[:shortMovingTicks]

        longTickList.insert(0, floatPrice(currentPrice))
        if len(longTickList) > longMovingTicks:
            longTickList = longTickList[:longMovingTicks]

        shortMAList.insert(0, getMeanFromList(shortTickList))
        if len(shortMAList) > 5:
            shortMAList = shortMAList[:5]

        longMAList.insert(0, getMeanFromList(longTickList))
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

        if counter > 10:
            if shortMAList[-1] < shortMAList[0]:
                shortMATrend = Trend.UP
            elif shortMAList[-1] > shortMAList[0]:
                shortMATrend = Trend.DOWN
            else:
                shortMATrend = Trend.DEFAULT

        # 趋势上扬并且短期向上穿越
        if lastLocalMAStatus == MARelation.BELOW and currentLocalMAStatus == MARelation.ABOVE and longMATrend == Trend.UP:
            MABuyInSignal = True
        else:
            MABuyInSignal = False

        # 短期趋势下降或短期向下穿越
        if (lastLocalMAStatus == MARelation.ABOVE and currentLocalMAStatus == MARelation.BELOW) or shortMATrend == Trend.DOWN:
            MASellOutSignal = True
        else:
            MASellOutSignal = False

        # ============== bollinger =================
        mean = (mean * counter + floatPrice(currentPrice)) / (counter + 1)
        variance = (variance * counter + (floatPrice(currentPrice) - mean) ** 2) / (counter + 1)
        standardDeviation = sqrt(variance)

        if floatPrice(currentPrice) > mean + bollingRadius * standardDeviation: #顶端
            pass
        elif floatPrice(currentPrice) > mean - bollingRadius * standardDeviation\
                and floatPrice(currentPrice) <= mean + bollingRadius * standardDeviation: # 带中
            pass
        else: #底部
            pass

        # ================= gear =====================
        gearArr = getGearData(connectSocket, stockCode, 1)
        if gearArr is not None:
            currentBuyOnePrice = floatPrice(gearArr[0]["BuyPrice"])
            currentBuyOneVol = float(gearArr[0]["BuyVol"])
            currentSellOnePrice = floatPrice(gearArr[0]["SellPrice"])
            currentSellOneVol = float(gearArr[0]["SellVol"])

            currentMidGearPrice = (currentBuyOnePrice + currentSellOnePrice) / 2
            if currentMidGearPrice != lastMidGearPrice:
                gearStableCounter = 0

            if gearStableCounter > 10:
                if currentBuyOneVol < currentSellOneVol:
                    if currentBuyOneVol < lastBuyOneVol and currentSellOneVol / currentBuyOneVol > 3: #买1被消耗
                        gearSellOutSignal = True
                    else:
                        gearSellOutSignal = False
                else:
                    if currentSellOneVol < lastSellOneVol and currentBuyOneVol / currentSellOneVol > 3: #卖1被消耗
                        gearBuyInSignal = True
                    else:
                        gearBuyInSignal = False

        # ============== strategy ======================

        if MABuyInSignal and gearBuyInSignal:
            buyInSignal = True
        else:
            buyInSignal = False

        if MASellOutSignal and gearSellOutSignal:
            sellOutSignal = True
        else:
            sellOutSignal = False

        # 止损
        if positionRatio < -0.03:
            sellOutSignal = True

        if buyInSignal:
            if not hasFullPosition:
                # sell_one = getSellPrice(connectSocket, stockCode, 1, 0)
                print "tag 2"
                hasBuyOrder = False
                orderInfoArr = simu_inquireOrder(connectSocket)
                print "tag 3"
                if orderInfoArr is not None:
                    for orderInfo in orderInfoArr:
                        if orderInfo["StockCode"] == stockCode and orderInfo["Status"] == "1":
                            if orderInfo["OrderSide"] == "0" and orderInfo["Price"] == currentPrice:
                                hasBuyOrder = True
                            else:
                                simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)#撤单
                                print "tag 4"

                if not hasBuyOrder:#如果没有未成交合适订单则下单
                    localID = simu_commonBuyOrder(connectSocket, currentPrice, tradeOneHand, stockCode)
                    print "tag 5"
                    orderID += 1
                    print "buy at", float(currentPrice) / 1000, "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID, "orderID", orderID
                    log = ["buy at ", str(float(currentPrice) / 1000), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, " orderID ", str(orderID), "\n"]
                    file = open("run log", "a+")
                    file.writelines(log)
                    file.close()

        elif sellOutSignal:
            if hasFullPosition:
                # buy_one = getBuyPrice(connectSocket, stockCode, 1, 0)
                print "tag 6"
                hasSellOrder = False
                orderInfoArr = simu_inquireOrder(connectSocket)
                print "tag 7"
                if orderInfoArr is not None:
                    for orderInfo in orderInfoArr:
                        if orderInfo["StockCode"] == stockCode and orderInfo["Status"] == "1":
                            if orderInfo["OrderSide"] == "1" and orderInfo["Price"] == currentPrice:
                                hasSellOrder = True
                            else:
                                simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)#撤单
                                print "tag 8"

                if not hasSellOrder:
                    localID = simu_commonSellOrder(connectSocket, currentPrice, tradeOneHand, stockCode)
                    print "tag 9"
                    orderID += 1
                    print "sell at", float(currentPrice) / 1000, "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID, "orderID", orderID
                    log = ["sell at ", str(float(currentPrice) / 1000), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, " orderID ", str(orderID), "\n"]
                    file = open("run log", "a+")
                    file.writelines(log)
                    file.close()

        # 更新需要记录的参数
        lastPrice = currentPrice
        counter += 1
        gearStableCounter += 1

        lastLocalMAStatus = currentLocalMAStatus

        lastBuyOnePrice = currentBuyOnePrice
        lastBuyOneVol = currentBuyOneVol
        lastSellOnePrice = currentSellOnePrice
        lastSellOneVol = currentSellOneVol

        lastMidGearPrice = currentMidGearPrice

        time.sleep(oneTickTime)
disconnect(connectSocket)

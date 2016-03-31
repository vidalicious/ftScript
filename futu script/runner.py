#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import FSApi
import time

# 先锋服务集团 "00500" 1000
# 中国太保 "02601" 200
# 腾讯控股 "00700" 100

host = "localhost"
port = 11111
stockCode = "02601"
tradeOneHand = 200

localID = 0
orderID = 1
lastPrice = 0
continuousRise = 0
continuousDrop = 0
fullPostion = False
count = 0
connectSocket = FSApi.connect(host, port)

if connectSocket is not None:
    while True:
        currentPrice = FSApi.getCurrentPrice(connectSocket, stockCode)
        print "currentPrice", float(currentPrice) / 1000, "count", count, "time", time.strftime('%Y-%m-%d %H:%M:%S')

        fullPostion = FSApi.simu_hasPosition(connectSocket, tradeOneHand, stockCode)
        # orderInfoArr = FSApi.simu_inquireOrder(connectSocket)

        if lastPrice != 0:

            if currentPrice > lastPrice:
                continuousRise += 1
                continuousDrop = 0
            elif currentPrice < lastPrice:
                continuousDrop += 1
                continuousRise = 0
            else:
                pass
        else:
            continuousRise = 0
            continuousDrop = 0

        if continuousRise > 1:
            if not fullPostion:
                sell_one = FSApi.getSellPrice(connectSocket, stockCode, 1, 0)
                hasBuyOrder = False
                orderInfoArr = FSApi.simu_inquireOrder(connectSocket)
                if orderInfoArr is not None:
	                for orderInfo in orderInfoArr:
	                    if orderInfo["StockCode"] == stockCode and orderInfo["Status"] == "1":
	                        if orderInfo["OrderSide"] == "0" and orderInfo["Price"] == sell_one:
	                            hasBuyOrder = True
	                        else:
	                            FSApi.simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)#撤单

                if not hasBuyOrder:#如果没有未成交合适订单则下单
                    localID = FSApi.simu_commonBuyOrder(connectSocket, sell_one, tradeOneHand, stockCode)
                    orderID += 1
                    print "buy at", float(sell_one) / 1000, "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID, "orderID", orderID
                    log = ["buy at ", str(float(sell_one) / 1000), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, " orderID ", orderID, "\n"]
                    file = open("run log", "a+")
                    file.writelines(log)
                    file.close()

        elif continuousDrop > 1:
            if fullPostion:
                buy_one = FSApi.getBuyPrice(connectSocket, stockCode, 1, 0)
                hasSellOrder = False
                orderInfoArr = FSApi.simu_inquireOrder(connectSocket)
                if orderInfoArr is not None:
	                for orderInfo in orderInfoArr:
	                    if orderInfo["StockCode"] == stockCode and orderInfo["Status"] == "1":
	                        if orderInfo["OrderSide"] == "1" and orderInfo["Price"] == buy_one:
	                            hasSellOrder = True
	                        else:
	                            FSApi.simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)#撤单

                if not hasSellOrder:
                    localID = FSApi.simu_commonSellOrder(connectSocket, buy_one, tradeOneHand, stockCode)
                    orderID += 1
                    print "sell at", float(buy_one) / 1000, "time", time.strftime('%Y-%m-%d %H:%M:%S'), "localID", localID, "orderID", orderID
                    log = ["sell at ", str(float(buy_one) / 1000), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, " orderID ", orderID, "\n"]
                    file = open("run log", "a+")
                    file.writelines(log)
                    file.close()

        # 更新价格
        lastPrice = currentPrice
        count += 1
        time.sleep(1)
FSApi.disconnect(connectSocket)

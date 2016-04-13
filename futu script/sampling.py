#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from FSApi import *
import time

host = "localhost"
port = 11111
stockCode = "01419"
tradeOneHand = 2000

oneTickTime = 3
count = 0
connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        file = open("data", "a+")
        # =============== current price =================
        currentPrice = getCurrentPrice(connectSocket, stockCode)
        print "currentPrice ", float(currentPrice) / 1000, " count ", count, " time ", time.strftime('%Y-%m-%d %H:%M:%S')
        log = ["currentPrice ", str(float(currentPrice) / 1000), " count ", str(count), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"]
        file.writelines(log)

        # =============== buy and sell ==================

        gearArr = getGearData(connectSocket, stockCode, 10)

        buyOrder = []
        buyPrice = []
        buyVol = []

        sellOrder = []
        sellPrice = []
        sellVol = []

        if gearArr is not None:
            for gear in gearArr:
                buyOrder.append(gear["BuyOrder"])
                buyPrice.append(gear["BuyPrice"])
                buyVol.append(gear["BuyVol"])

                sellOrder.append(gear["SellOrder"])
                sellPrice.append(gear["SellPrice"])
                sellVol.append(gear["SellVol"])

        if buyPrice is not None:
            for i in range(len(buyPrice)):
                print "buy ", i + 1, " order ", buyOrder[i], " price ", floatPrice(buyPrice[i]), " vol ", buyVol[i]
                log = ["buy ", str(i + 1), " order ", buyOrder[i], " price ", str(floatPrice(buyPrice[i])), " vol ", buyVol[i], "\n"]
                file.writelines(log)

                print "sell ", i + 1, " order ", sellOrder[i], " price ", floatPrice(sellPrice[i]), " vol ", sellVol[i]
                log = ["sell ", str(i + 1), " order ", sellOrder[i], " price ", str(floatPrice(sellPrice[i])), " vol ", sellVol[i], "\n"]
                file.writelines(log)

            log = ["=========================================================================================="]
            file.writelines(log)

        file.close()
        count += 1
        time.sleep(oneTickTime)
disconnect(connectSocket)
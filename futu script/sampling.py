#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import pandas as pd
import time
from FSApi import *
from math import *

host = "localhost"
port = 11111

targetCode = "69343" #恒指

oneTickTime = 1
counter = 0

ema10sCount = 10 / oneTickTime #10秒
ema1Count = 60 / oneTickTime # 1分钟的tick数
ema2Count = 60 * 2 / oneTickTime
ema3Count = 60 * 3 / oneTickTime
ema5Count = 60 * 5 / oneTickTime #5分钟tick
ema10Count = 60 * 10 / oneTickTime
ema15Count = 60 * 15 / oneTickTime
ema20Count = 60 * 20 / oneTickTime
ema30Count = 60 * 30 / oneTickTime
ema45Count = 60 * 45 / oneTickTime
ema60Count = 60 * 60 / oneTickTime

ema10s_K = float(2.0 / (ema10sCount + 1))
ema1_K = float(2.0 / (ema1Count + 1))
ema2_K = float(2.0 / (ema2Count + 1))
ema3_K = float(2.0 / (ema3Count + 1))
ema5_K = float(2.0 / (ema5Count + 1))
ema10_K = float(2.0 / (ema10Count + 1))
ema15_K = float(2.0 / (ema15Count + 1))
ema20_K = float(2.0 / (ema20Count + 1))
ema30_K = float(2.0 / (ema30Count + 1))
ema45_K = float(2.0 / (ema45Count + 1))
ema60_K = float(2.0 / (ema60Count + 1))

mean10s = 0
mean1 = 0
mean2 = 0
mean3 = 0
mean5 = 0
mean10 = 0
mean15 = 0
mean20 = 0
mean30 = 0
mean45 = 0
mean60 = 0

lastMean5 = 0

energy5 = 0

meank5 = 0

targetList = []

connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        if not isGameBegin():
            continue
        elif isInMidRestTime():
            continue
        elif datetime.datetime.now().time() > datetime.time(16, 0, 1):
            break

        currentTarget = getCurrentPrice(connectSocket, targetCode)
        print "counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')

        targetList.insert(0, floatPrice(currentTarget))
        if len(targetList) > 60 * 60:
            targetList = targetList[:60 * 60]

        bullBuy1Price = ""
        bullSell1Price = ""
        bullGearArr = getGearData(connectSocket, targetCode, 1)
        if bullGearArr is not None:
            bullBuy1Price = bullGearArr[0]["BuyPrice"]
            bullSell1Price = bullGearArr[0]["SellPrice"]

        mean10s = updateMeanBy(floatPrice(currentTarget), ema10s_K, mean10s)
        mean1 = updateMeanBy(floatPrice(currentTarget), ema1_K, mean1)
        mean2 = updateMeanBy(floatPrice(currentTarget), ema2_K, mean2)
        mean3 = updateMeanBy(floatPrice(currentTarget), ema3_K, mean3)
        mean5 = updateMeanBy(floatPrice(currentTarget), ema5_K, mean5)
        mean10 = updateMeanBy(floatPrice(currentTarget), ema10_K, mean10)
        mean15 = updateMeanBy(floatPrice(currentTarget), ema15_K, mean15)
        mean20 = updateMeanBy(floatPrice(currentTarget), ema20_K, mean20)
        mean30 = updateMeanBy(floatPrice(currentTarget), ema30_K, mean30)
        mean45 = updateMeanBy(floatPrice(currentTarget), ema45_K, mean45)
        mean60 = updateMeanBy(floatPrice(currentTarget), ema60_K, mean60)

        variance60 = getVarianceFromList(targetList, mean60)
        sd60 = sqrt(variance60)

        lt = []
        lbuy1 = []
        lsell1 = []
        l10s = []
        l1 = []
        l2 = []
        l3 = []
        l5 = []
        l10 = []
        l15 = []
        l20 = []
        l30 = []
        l45 = []
        l60 = []
        lsd60 = []

        lIndex = []

        lt.append(floatPrice(currentTarget))
        lbuy1.append(floatPrice(bullBuy1Price))
        lsell1.append(floatPrice(bullSell1Price))
        l10s.append(mean10s)
        l1.append(mean1)
        l2.append(mean2)
        l3.append(mean3)
        l5.append(mean5)
        l10.append(mean10)
        l15.append(mean15)
        l20.append(mean20)
        l30.append(mean30)
        l45.append(mean45)
        l60.append(mean60)
        lsd60.append(sd60)

        lIndex.append(counter)

        st = pd.Series(lt, index=lIndex)
        sbuy1 = pd.Series(lbuy1, index=lIndex)
        ssell1 = pd.Series(lsell1, index=lIndex)
        s10s = pd.Series(l10s, index=lIndex)
        s1 = pd.Series(l1, index=lIndex)
        s2 = pd.Series(l2, index=lIndex)
        s3 = pd.Series(l3, index=lIndex)
        s5 = pd.Series(l5, index=lIndex)
        s10 = pd.Series(l10, index=lIndex)
        s15 = pd.Series(l15, index=lIndex)
        s20 = pd.Series(l20, index=lIndex)
        s30 = pd.Series(l30, index=lIndex)
        s45 = pd.Series(l45, index=lIndex)
        s60 = pd.Series(l60, index=lIndex)
        ssd60 = pd.Series(lsd60, index=lIndex)

        d = {"st" : st,
             "buy1" : sbuy1,
             "sell1" : ssell1,
             "s10s" : s10s,
             "s1" : s1,
             "s2" : s2,
             "s3" : s3,
             "s5" : s5,
             "s10" : s10,
             "s15" : s15,
             "s20" : s20,
             "s30" : s30,
             "s45" : s45,
             "s60" : s60,
             "sd60" : ssd60
        }

        df = pd.DataFrame(d)

        if counter == 0:
            hasHead = True
        else:
            hasHead = False
        with open("sampling.csv", "a+") as f:
            df.to_csv(f, header=hasHead)

        counter += 1
        lastMean5 = mean5
        time.sleep(oneTickTime)
    disconnect(connectSocket)

#
# l0 = []
# l1 = []
# for i in range(0, 10):
#     l0.append(i)
#     l1.append(-i)
#
# s0 = pd.Series(l0)
# s1 = pd.Series(l1)
#
# d = {"s0" : s0, "s1" : s1}
# df = pd.DataFrame(d)
#
# with open("sampling.csv", "a+") as f:
#     df.to_csv(f, header=False)

# pd.set_option('display.max_rows', len(s))
# print s
# pd.reset_option('display.max_rows')
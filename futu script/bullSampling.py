#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import pandas as pd
import time
from FSApi import *
from math import *

# 恒指法兴七七牛   67314   20008

host = "localhost"
port = 11111

targetCode = "67314" #恒指

oneTickTime = 1
counter = 0

ema10sCount = 10 / oneTickTime #10秒
ema1Count = 60 / oneTickTime # 1分钟的tick数
ema5Count = 60 * 5 / oneTickTime #5分钟tick
ema10Count = 60 * 10 / oneTickTime
ema15Count = 60 * 15 / oneTickTime
ema20Count = 60 * 20 / oneTickTime
ema30Count = 60 * 30 / oneTickTime
ema45Count = 60 * 45 / oneTickTime
ema60Count = 60 * 60 / oneTickTime

ema10s_K = float(2.0 / (ema10sCount + 1))
ema1_K = float(2.0 / (ema1Count + 1))
ema5_K = float(2.0 / (ema5Count + 1))
ema10_K = float(2.0 / (ema10Count + 1))
ema15_K = float(2.0 / (ema15Count + 1))
ema20_K = float(2.0 / (ema20Count + 1))
ema30_K = float(2.0 / (ema30Count + 1))
ema45_K = float(2.0 / (ema45Count + 1))
ema60_K = float(2.0 / (ema60Count + 1))

mean10s = 0
mean1 = 0
mean5 = 0
mean10 = 0
mean15 = 0
mean20 = 0
mean30 = 0
mean45 = 0
mean60 = 0

connectSocket = connect(host, port)
if connectSocket is not None:
    while True:
        if not isGameBegin():
            continue
        elif datetime.datetime.now().time() > datetime.time(16, 0, 1):
            break

        currentTarget = getCurrentPrice(connectSocket, targetCode)
        print "counter ", str(counter), " target ", str(floatPrice(currentTarget)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')
        mean10s = updateMeanBy(floatPrice(currentTarget), ema10s_K, mean10s)
        mean1 = updateMeanBy(floatPrice(currentTarget), ema1_K, mean1)
        mean5 = updateMeanBy(floatPrice(currentTarget), ema5_K, mean5)
        mean10 = updateMeanBy(floatPrice(currentTarget), ema10_K, mean10)
        mean15 = updateMeanBy(floatPrice(currentTarget), ema15_K, mean15)
        mean20 = updateMeanBy(floatPrice(currentTarget), ema20_K, mean20)
        mean30 = updateMeanBy(floatPrice(currentTarget), ema30_K, mean30)
        mean45 = updateMeanBy(floatPrice(currentTarget), ema45_K, mean45)
        mean60 = updateMeanBy(floatPrice(currentTarget), ema60_K, mean60)

        lt = []
        l10s = []
        l1 = []
        l5 = []
        l10 = []
        l15 = []
        l20 = []
        l30 = []
        l45 = []
        l60 = []
        lIndex = []

        lt.append(floatPrice(currentTarget))
        l10s.append(mean10s)
        l1.append(mean1)
        l5.append(mean5)
        l10.append(mean10)
        l15.append(mean15)
        l20.append(mean20)
        l30.append(mean30)
        l45.append(mean45)
        l60.append(mean60)
        lIndex.append(counter)

        st = pd.Series(lt, index=lIndex)
        s10s = pd.Series(l10s, index=lIndex)
        s1 = pd.Series(l1, index=lIndex)
        s5 = pd.Series(l5, index=lIndex)
        s10 = pd.Series(l10, index=lIndex)
        s15 = pd.Series(l15, index=lIndex)
        s20 = pd.Series(l20, index=lIndex)
        s30 = pd.Series(l30, index=lIndex)
        s45 = pd.Series(l45, index=lIndex)
        s60 = pd.Series(l60, index=lIndex)

        d = {"st" : st,
             "s10s" : s10s,
             "s1" : s1,
             "s5" : s5,
             "s10" : s10,
             "s15" : s15,
             "s20" : s20,
             "s30" : s30,
             "s45" : s45,
             "s60" : s60}

        df = pd.DataFrame(d)

        with open("bull sampling.csv", "a+") as f:
            df.to_csv(f, header=False)

        counter += 1
        time.sleep(oneTickTime)
    disconnect(connectSocket)
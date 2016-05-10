#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import FSApi

# 先锋服务集团 "00500" 1000
# 中国太保 "02601" 200

host = "localhost"
port = 11111
stockCode = "63252"
tradeOneHand = 10000

connectSocket = FSApi.connect(host, port)
buy_one = FSApi.getBuyPrice(connectSocket, stockCode, 1, 0)
localID = FSApi.simu_commonSellOrder(connectSocket, buy_one, tradeOneHand, stockCode)
FSApi.disconnect(connectSocket)
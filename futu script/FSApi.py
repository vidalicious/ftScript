#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import FSSender
import socket
import datetime
import time

# ====================================== CONNECTION ==================================
COOKIE = 1

def connect(host, port):
	try:
		connectSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connectSocket.settimeout(2)
		connectSocket.connect((host, port))
		connectSocket.settimeout(None)
	except Exception as e:
		print("连接错误")
		print(e)
		return
	return connectSocket

def disconnect(connectSocket):
    connectSocket.close()

# ================================= COMMON =======================================

def getCurrentPrice(connectSocket, stockCode):
	return getBasicData(connectSocket, stockCode)["Cur"]

def getSellPrice(connectSocket, stockCode, gearNum, gearIndex):
	return getGearData(connectSocket, stockCode, gearNum)[gearIndex]["SellPrice"]

def getBuyPrice(connectSocket, stockCode, gearNum, gearIndex):
	return getGearData(connectSocket, stockCode, gearNum)[gearIndex]["BuyPrice"]


def getBasicData(connectSocket, stockCode):
	req_param = {"Market": "1", "StockCode": stockCode}
	response = FSSender.send_req_and_get_rsp(connectSocket, "1001", req_param, 1)
	if int(response[0]["ErrCode"]) == 0:
		if response[0]["RetData"] is not None:
			return response[0]["RetData"]


def getGearData(connectSocket, stockCode, gearNum):
	requestPara = {"Market": "1", "StockCode": stockCode, "GetGearNum":str(gearNum)}
	response = FSSender.send_req_and_get_rsp(connectSocket, "1002", requestPara, 1)
	if(int(response[0]["ErrCode"]) == 0):
		if(response[0]["RetData"] is not None):
			return response[0]["RetData"]["GearArr"]

# envType 0 真实 1 仿真
# orderSide 0 买入 1 卖出
def placeOrder(connectSocket, envType, orderSide, orderType, price, quality, stockCode):
	global COOKIE
	requestPara = {"Cookie": str(COOKIE), "EnvType": str(envType), "OrderSide": str(orderSide), "OrderType": str(orderType), "Price": str(price), "Qty": str(quality), "StockCode": stockCode}
	updateCookie()
	response = FSSender.send_req_and_get_rsp(connectSocket, "6003", requestPara, 1)

	orderSuccess = True
	localID = "0"
	if response is not None:
		for rsp in response:
			if int(rsp["ErrCode"]) == 0:
				localID = rsp["RetData"]["LocalID"]
			else:
				orderSuccess = False
				print rsp["ErrDesc"]
	if orderSuccess:
		print "place order success!"
	return localID

# setOrderStatus 0 撤单 1 失效 2 生效 3 删除
def setOrderStatus(connectSocket, envType, localID, orderID, setStatus):
	global COOKIE
	requestPara = {"Cookie": str(COOKIE), "EnvType": str(envType), "LocalID": str(localID), "OrderID": str(orderID), "SetOrderStatus": str(setStatus)}
	updateCookie()
	response = FSSender.send_req_and_get_rsp(connectSocket, "6004", requestPara, 1)

	setStatusSuccess = True
	if int(response[0]["ErrCode"]) == 0:
		setStatusSuccess = True
		print "set status success"
	else:
		setStatusSuccess = False
		print response[0]["ErrDesc"]

	return setStatusSuccess

def modifyOrder(connectSocket, envType, localID, orderID, price, quantity):
	global COOKIE
	requestPara = {"Cookie": str(COOKIE), "EnvType": str(envType), "LocalID": str(localID), "OrderID": str(orderID), "Price": str(price), "Qty": str(quantity)}
	updateCookie()
	response = FSSender.send_req_and_get_rsp(connectSocket, "6005", requestPara, 1)
	if int(response[0]["ErrCode"]) == 0:
		print "modify order success"
	else:
		print response[0]["ErrDesc"]

def inquirePosition(connectSocket, envType):
	global COOKIE
	requestPara = {"Cookie": str(COOKIE), "EnvType": str(envType)}
	updateCookie()
	response = FSSender.send_req_and_get_rsp(connectSocket,"6009", requestPara, 1)

	if int(response[0]["ErrCode"]) == 0:
		if response[0]["RetData"] is not  None:
			return response[0]["RetData"]["HKPositionArr"]
	else:
		print response[0]["ErrDesc"]

def inquireOrder(connectSocket, envType):
	global COOKIE
	requestPara = {"Cookie": str(COOKIE), "EnvType": str(envType)}
	updateCookie()
	response = FSSender.send_req_and_get_rsp(connectSocket, "6008", requestPara, 1)

	if int(response[0]["ErrCode"]) == 0:
		if response[0]["RetData"] is not None:
			return response[0]["RetData"]["HKOrderArr"]
	else:
		print response[0]["ErrDesc"]

# ================================= SIMULATION ================================
def simu_commonBuyOrder(connectSocket, price, quality, stockCode):
	return simu_placeOrder(connectSocket, 0, 0, price, quality, stockCode)

def simu_commonSellOrder(connectSocket, price, quality, stockCode):
	return simu_placeOrder(connectSocket, 1, 0, price, quality, stockCode)

def simu_placeOrder(connectSocket, orderSide, orderType, price, quality, stockCode):
	return placeOrder(connectSocket, 1, orderSide, orderType, price, quality, stockCode)

def simu_setOrderStatus(connectSocket, localID, orderID, setStatus):
	return setOrderStatus(connectSocket, 1, localID, orderID, setStatus)

def simu_modifyOrder(connectSocket, localID, orderID, price, quantity):
	return modifyOrder(connectSocket, 1, localID, orderID, price, quantity)

def simu_inquirePosition(connectSocket):
	return inquirePosition(connectSocket, 1)

def simu_inquireOrder(connectSocket):
	return inquireOrder(connectSocket, 1)

def simu_checkOrderAndBuyWith(connectSocket, price, quantity, stockCode, file, pathTag):
	hasBuyOrder = False
	orderInfoArr = simu_inquireOrder(connectSocket)
	tradePrice = price
	if orderInfoArr is not None:
		for orderInfo in orderInfoArr:
			if orderInfo["StockCode"] == stockCode and (orderInfo["Status"] == "0" or orderInfo["Status"] == "1"):
				if orderInfo["OrderSide"] == "0":
					hasBuyOrder = True
					if orderInfo["Price"] == tradePrice:
						pass
					else:
						# 价格不对修改订单
						simu_modifyOrder(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], tradePrice, quantity)
						print "modify stock ", stockCode, " buy order to ", str(floatPrice(tradePrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')
						logger = ["modify stock ", stockCode, " buy order to ", str(floatPrice(tradePrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"]
						file.writelines(logger)
				else:
					hasBuyOrder = True # 有卖单，不再买，先卖
					# simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)  # 撤单
					# pathTag.append(" 撤卖单 ")

	if not hasBuyOrder:  # 如果没有未成交合适订单则下单
		localID = simu_commonBuyOrder(connectSocket, tradePrice, quantity, stockCode)
		print "buy stock ", stockCode, " at ", floatPrice(tradePrice), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID
		logger = ["buy stock ", stockCode, " at ", str(floatPrice(tradePrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, "\n"]
		file.writelines(logger)
		pathTag.append("\n")
		file.writelines(pathTag)

def simu_checkOrderAndSellWith(connectSocket, price, quantity, stockCode, file, pathTag):
	hasSellOrder = False
	orderInfoArr = simu_inquireOrder(connectSocket)
	tradePrice = price
	if orderInfoArr is not None:
		for orderInfo in orderInfoArr:
			if orderInfo["StockCode"] == stockCode and (orderInfo["Status"] == "0" or orderInfo["Status"] == "1"):
				if orderInfo["OrderSide"] == "1":
					hasSellOrder = True
					if orderInfo["Price"] == tradePrice:
						pass
					else:
						# 价格不对修改订单
						simu_modifyOrder(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], tradePrice, quantity)
						print "modify stock ", stockCode, " sell order to ", str(floatPrice(tradePrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S')
						logger = ["modify stock ", stockCode, "sell order to ", str(floatPrice(tradePrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), "\n"]
						file.writelines(logger)
				else:
					simu_setOrderStatus(connectSocket, orderInfo["LocalID"], orderInfo["OrderID"], 0)  # 撤单
					pathTag.append(" 撤买单 ")

	if not hasSellOrder:
		localID = simu_commonSellOrder(connectSocket, tradePrice, quantity, stockCode)
		print "sell stock ", stockCode, " at ", floatPrice(tradePrice), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID
		logger = ["sell stock ", stockCode, " at ", str(floatPrice(tradePrice)), " time ", time.strftime('%Y-%m-%d %H:%M:%S'), " localID ", localID, "\n"]
		file.writelines(logger)
		pathTag.append("\n")
		file.writelines(pathTag)

# # 	是否有关于该股票的仓位
# def simu_hasPosition(connectSocket, quality, stockCode):
# 	positionArr = simu_inquirePosition(connectSocket)
# 	hasPosition = False
# 	if positionArr is not None:
# 		for position in positionArr:
# 			if stockCode == position["StockCode"] and int(position["CanSellQty"]) >= int(quality):
# 				hasPosition = True
# 				break
# 	return hasPosition
# ================================= REAL ==================================

# ================================= UTIL ==================================
def updateCookie():
	global COOKIE
	COOKIE += 1

def floatPrice(price):
    return float(price) / 1000

def strPriceFromFloat(price):
	return str(price * 1000)

def getMeanFromList(list):
	total = 0
	if list is not None:
		for price in list:
			total += price
		return total / len(list)
	else:
		return 0

def getVarianceFromList(list, mean):
	total = 0
	if list is not None:
		for i in list:
			total += (i - mean) ** 2
		return total / len(list)
	else:
		return 0

def getAverageBiasFromList(list, mean):
	total = 0
	if list is not None:
		for i in list:
			total += (i - mean)
		return total / len(list)
	else:
		return 0

# 	是否有关于该股票的仓位
def ifHasPositon(positionArr, quality, stockCode):
	hasPosition = False
	if positionArr is not None:
		for position in positionArr:
			if stockCode == position["StockCode"] and int(position["CanSellQty"]) >= int(quality):
				hasPosition = True
				break
	return hasPosition

def getPositionPrice(positionArr, stockCode):
	if positionArr is not None:
		for position in positionArr:
			if position["StockCode"] == stockCode:
				return position["CostPrice"]
	return "0"

def getPositionRatio(positionArr, stockCode):
	if positionArr is not None:
		for position in positionArr:
			if position["StockCode"] == stockCode:
				return float(position["PLRatio"]) / 100000
	return 0

def isGameBegin():
	if datetime.datetime.now().time() > datetime.time(9, 29, 0):
		return True
	else:
		return False

def isInGoldenTime():
	if datetime.datetime.now().time() > datetime.time(9, 32, 0) and datetime.datetime.now().time() < datetime.time(11, 0, 0):
		return True
	else:
		return False

def isInWarningTime():
	if datetime.datetime.now().time() > datetime.time(15, 58, 0):
		return True
	else:
		return False

def isTimeToExit():
	if datetime.datetime.now().time() > datetime.time(16, 0, 0):
		return True
	else:
		return False

def priceMoveUnit(price):
	if price <= 0.25:
		return 0.001 #价格[0.05, 0.25] 单位幅度变化0.4%-2%
	if price > 0.25 and price <= 0.5:
		return 0.005
	if price > 0.5 and price <= 10:
		return 0.01
	if price > 10 and price <= 20:
		return 0.02
	if price > 20 and price <= 100:
		return 0.05
	if price > 100 and price <= 200:
		return 0.1
	if price > 200 and price <= 500:
		return 0.2
	if price > 500 and price <= 1000:
		return 0.5
	if price > 1000 and price <= 2000:
		return 1.0
	if price > 2000:
		return 2.0
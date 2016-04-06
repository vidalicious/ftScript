#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import FSSender
import socket

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
	COOKIE += 1
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
	COOKIE += 1
	response = FSSender.send_req_and_get_rsp(connectSocket, "6004", requestPara, 1)

	setStatusSuccess = True
	if int(response[0]["ErrCode"]) == 0:
		setStatusSuccess = True
		print "set status success"
	else:
		setStatusSuccess = False
		print response[0]["ErrDesc"]

	return setStatusSuccess


def inquirePosition(connectSocket, envType):
	global COOKIE
	requestPara = {"Cookie": str(COOKIE), "EnvType": str(envType)}
	COOKIE += 1
	response = FSSender.send_req_and_get_rsp(connectSocket,"6009", requestPara, 1)

	if int(response[0]["ErrCode"]) == 0:
		if response[0]["RetData"] is not  None:
			return response[0]["RetData"]["HKPositionArr"]
	else:
		print response[0]["ErrDesc"]

def inquireOrder(connectSocket, envType):
	global COOKIE
	requestPara = {"Cookie": str(COOKIE), "EnvType": str(envType)}
	COOKIE += 1
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

def simu_inquirePosition(connectSocket):
	return inquirePosition(connectSocket, 1)

def simu_inquireOrder(connectSocket):
	return inquireOrder(connectSocket, 1)

# 	是否有关于该股票的仓位
def simu_hasPosition(connectSocket, quality, stockCode):
	positionArr = simu_inquirePosition(connectSocket)
	hasPosition = False
	if positionArr is not None:
		for position in positionArr:
			if stockCode == position["StockCode"] and int(position["CanSellQty"]) >= int(quality):
				hasPosition = True
				break
	return hasPosition
# ================================= REAL ==================================

# ================================= UTIL ==================================
def floatPrice(price):
    return float(price) / 1000
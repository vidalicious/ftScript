#!/usr/bin/python
# -*- coding: utf-8 -*-  
'''
Created on 2015��11��5��
#�ű�˵��: !!!
#
#��װ������api�ӿ�
#1. connect_to_futunn_api  
#2. disconnect 
#3. json_analyze_rsps  
#4. send_req_and_get_rsp  
#5. get_stock_base_price
#6. get_stock_gear
#7. place_order 
#
@author: futu
'''

import socket
import json
import string
import sys

#����:IP, �˿�
#����:Socket
def connect_to_futunn_api(host, port):
	try:
		socket_futu_api = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		socket_futu_api.settimeout(2)
		socket_futu_api.connect((host, port))
		socket_futu_api.settimeout(None)
	except Exception as e:
		print("���Ӵ���")
		print(e)
		return
	return socket_futu_api


def disconnect(socket_futu_api):
	socket_futu_api.close()


def json_analyze_rsps(rsp_str):
	ret_data_arr = []
	rsp_ar = rsp_str.split("\r\n") 
	for rsp in rsp_ar:
		if(len(rsp) <= 0):
			continue
		rsp_after_json_analyze = json.loads(rsp)
		ret_data_arr.append(rsp_after_json_analyze)
	return ret_data_arr
	
#����:Э���, ����, �汾��
#����:�ذ�
def send_req_and_get_rsp(socket_futu_api, protocol_code, req_param, protocol_version):
	#����
	try:
		req = {"Protocol":str(protocol_code), "ReqParam":req_param, "Version":str(protocol_version)}
		req_str = json.dumps(req) + "\r\n"
		socket_futu_api.send(req_str)
	except socket.timeout:
		return
	
	buf_size = 50
	#�հ�
	rsp_str = ""
	while True:
		buf = socket_futu_api.recv(int(buf_size))
		rsp_str += buf
		if(len(buf) < int(buf_size)):
			break

	#�ذ�josn����
	return json_analyze_rsps(rsp_str)


#����:�׽���, ��Ʊ����
#����:�ֵ�
#{str:int32}
#��ֵ:High, Open, Low, Close, Cur, LastClose, Turnover, Vol
def get_stock_base_price(socket_futu_api, stock_code):
	req_param = {"Market":"1", "StockCode": stock_code}
	analyzed_rsps = send_req_and_get_rsp(socket_futu_api, "1001", req_param, 1)
	
	if(int(analyzed_rsps[0]["ErrCode"]) == 0):
		if(analyzed_rsps[0]["RetData"] is not None):
			return analyzed_rsps[0]["RetData"]


#����:�׽���, ��Ʊ����, ������
#����:�б��ֵ�
#[{str:int32}]
#��ֵ:BuyOrder, BuyPrice, BuyVol, SellOrder, SellPrice,SellVol
def get_stock_gear(socket_futu_api, stock_code, get_gear_num):
	req_param = {"Market":"1", "StockCode":stock_code, "GetGearNum":str(get_gear_num)}
	analyzed_rsps = send_req_and_get_rsp(socket_futu_api, "1002", req_param, 1)
	
	if(int(analyzed_rsps[0]["ErrCode"]) == 0):
		if(analyzed_rsps[0]["RetData"] is not None):
			return analyzed_rsps[0]["RetData"]["GearArr"]


COOKIE = 8888
#����:�׽���, ���׻���(0:��ʵ,1:����), ���׷���(0:��,1:��), ��������, ���׼۸�, ��������, ��Ʊ����
def place_order(socket_futu_api, evn_type, order_side, order_type, price, qty, stock_code):
	global COOKIE
	req_param = {"EnvType":str(evn_type), "Cookie":str(COOKIE), "OrderSide":str(order_side), "OrderType":str(order_type), "Price":str(price), "Qty":str(qty), "StockCode":stock_code}
	COOKIE += 1
	
	analyzed_rsps_arr = send_req_and_get_rsp(socket_futu_api, "6003", req_param, 1)
	
	order_success = True
	if(analyzed_rsps_arr is not None):
		for analyzed_rsps in analyzed_rsps_arr:
			if(int(analyzed_rsps["ErrCode"]) != 0):
				order_success = False 
				print(analyzed_rsps["ErrDesc"])
	
	if(order_success):
		print("���׳ɹ�")
	
	return order_success
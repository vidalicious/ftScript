#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket
import json

# ====================================================== JSON ===================================================

def json_analyze_rsps(rsp_str):
	ret_data_arr = []
	rsp_ar = rsp_str.split("\r\n")
	for rsp in rsp_ar:
		if(len(rsp) <= 0):
			continue
		rsp_after_json_analyze = json.loads(rsp)
		ret_data_arr.append(rsp_after_json_analyze)
	return ret_data_arr

#传入:协议号, 参数, 版本号
#返回:回包
def send_req_and_get_rsp(socket_futu_api, protocol_code, req_param, protocol_version):
	#发包
	try:
		req = {"Protocol":str(protocol_code), "ReqParam":req_param, "Version":str(protocol_version)}
		req_str = json.dumps(req) + "\r\n"
		socket_futu_api.send(req_str)
	except socket.timeout:
		return

	buf_size = 1024#50
	#收包
	rsp_str = ""
	while True:
		buf = socket_futu_api.recv(int(buf_size))
		rsp_str += buf
		if(len(buf) < int(buf_size)):
			break

	#回包josn解析
	return json_analyze_rsps(rsp_str)


#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
'''
Created on 2015��11��5��
#�ű�˵��: !!!
#
#����Ѷ�ļ۸񵽴�145��ʱ������һ�ļ۸�����100��!
#
@author: futu
'''

import futu_comom_api
import time

buy_condition_price = 145 * 1000
stock_code = "00700"
buy_num = 100

socket_to_futu_api = futu_comom_api.connect_to_futunn_api("localhost", 11111)
if(socket_to_futu_api is not None):
	while True:
		#��ȡ��ǰ�۸�
		dic_base_price = futu_comom_api.get_stock_base_price(socket_to_futu_api, stock_code)
		if(dic_base_price is None):
			print("��ȡ��ǰ�۸����")
			time.sleep(5)
			continue
		cur_price = dic_base_price["Cur"]

		#���۸񵽴�����
		if(int(cur_price) >= int(buy_condition_price)):
			print(("��Ʊ:%s��ǰ�۸�Ϊ%0.3f,����%0.3f") % (stock_code, (float(cur_price))/1000, (float(buy_condition_price))/1000))
			#��ȡ��һ�۸�
			dic_gear_info_arr = futu_comom_api.get_stock_gear(socket_to_futu_api, stock_code, 1)
			if(dic_gear_info_arr is None):
				print("��ȡ�������ڴ���")
				break
			sell_price_one = dic_gear_info_arr[0]["SellPrice"]
			
			#����
			print(("����һ�۸�%0.3f����%d��") % ((float(sell_price_one))/1000, int(buy_num)))
			futu_comom_api.place_order(socket_to_futu_api, 1, 0, 0, sell_price_one, buy_num, stock_code)
			break
		#��ѯ
		time.sleep(1)
	futu_comom_api.disconnect(socket_to_futu_api)
raw_input("��������˳�")

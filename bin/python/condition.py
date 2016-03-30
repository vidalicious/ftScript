#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
'''
Created on 2015��11��5��
#�ű�˵��: !!!
#
#����Ѷ�ļ۸񵽴�145��ʱ�򣬿�ʼִ�������ж�
# i.���������
#   1.����һ145��ʱ������100��
#   2.����һ150��ʱ������100��
#   3.����һ155��ʱ������100��
# ii.�����������У�������¼ۣ�
#   1.��¼һ����߼ۣ�Ȼ�����߼ۿ�ʼ�ж�
#      a.��2���ʱ������һ�ļ۸���100��
#      b.��3���ʱ������һ�ļ۸���100��
#      c.��4���ʱ������һ�ļ۸���100��
#   2.�����¼۵���140��ʱ��
#      a.����һ�ļ۸�ȫ������
#
@author: futu
'''


import futu_comom_api
import time

stock_code = "00700"
buy_num = 100
sell_num = 100

first_condition_price = 145 * 1000
buy_info_arr = [{"price":145 * 1000, "had_done":False}, {"price":150 * 1000, "had_done":False}, {"price":155 * 1000, "had_done":False}]
sell_info_arr =  [{"drop":2 * 1000, "had_done":False}, {"drop":3 * 1000, "had_done":False}, {"drop":4 * 1000, "had_done":False}]
all_sell_condition_price = 140 * 1000

hold_total = 0
highest_price = 0

socket_to_futu_api = futu_comom_api.connect_to_futunn_api("localhost", 11111)
if(socket_to_futu_api is not None):
	while True:
		#��ȡ��ǰ�۸�
		dic_base_price = futu_comom_api.get_stock_base_price(socket_to_futu_api, stock_code)
		if(dic_base_price is None):
			print("��ȡ��ǰ�۸����\r\n")
			continue
		cur_price = dic_base_price["Cur"]
		
		#��¼��ߵ�ǰ��
		highest_price = max(int(cur_price), int(highest_price))
		
		#��ȡ����������Ϣ
		dic_gear_info_arr = futu_comom_api.get_stock_gear(socket_to_futu_api, stock_code, 1)
		if(dic_gear_info_arr is None):
			print("��ȡ�������ڴ���\r\n")
			break
		
		#��ȡ��һ��һ
		buy_price_one = dic_gear_info_arr[0]["BuyPrice"]
		sell_price_one = dic_gear_info_arr[0]["SellPrice"]
		
		#���۸񵽴���������ǰ������
		if(int(cur_price) >= int(first_condition_price)):
			#�ж���������
			for buy_info in buy_info_arr:
				#û����������뵽������
				if(bool(buy_info["had_done"]) is False and int(sell_price_one) >= int(buy_info["price"])):
					print ("��Ʊ:%s��ǰ�۸�Ϊ%0.3f,����%0.3f") % (stock_code, (float(cur_price)) / 1000, (float(first_condition_price)) / 1000 )
					print("���ҵ�ǰ��һ�۸�Ϊ%0.3f,����%0.3f") % ((float(sell_price_one)) / 1000, (float(buy_info["price"])) / 1000)
					print(("����һ�۸�%0.3f����%d��") % ((float(sell_price_one))/1000, int(buy_num)))
					
					if(futu_comom_api.place_order(socket_to_futu_api, 1, 0, 0, sell_price_one, buy_num, stock_code)):
						buy_info["had_done"] = True
						hold_total = int(hold_total) + int(buy_num)
					print(("��ǰ����%d��\r\n\r\n") % hold_total)
			
			#�ж���������
			for sell_info in sell_info_arr:
				if(bool(sell_info["had_done"]) is False and int(highest_price) - int(cur_price) >= sell_info["drop"] and int(hold_total) > 0):
					print("��Ʊ:%s��ǰ�۸�Ϊ%0.3f,����%0.3f") % (stock_code, (float(cur_price)) / 1000, (float(first_condition_price)) / 1000 )
					print("���ҵ�ǰ�۸���뵱ǰ�۸���߳���%0.3f") % ((float(sell_info["drop"])) / 1000)
					print(("����һ�۸�%0.3f����%d��") % ((float(buy_price_one))/1000, int(cur_sell_num)))
					
					if(futu_comom_api.place_order(socket_to_futu_api, 1, 1, 0, buy_price_one, cur_sell_num, stock_code)):
						sell_info["had_done"] = True
						cur_sell_num = min(int(sell_num), int(hold_total))
						hold_total = int(hold_total) - int(cur_sell_num)
					print(("��ǰ����%d��\r\n") % hold_total)
		
			#�ж��Ƿ�ȫ������������
			conditon_trade_all_done = True
			for buy_info in buy_info_arr:
				if(bool(buy_info["had_done"]) is False):
					conditon_trade_all_done = False
					break
			
			for sell_info in sell_info_arr:
				if(bool(sell_info["had_done"]) is False):
					conditon_trade_all_done = False
					break
			
			if(bool(conditon_trade_all_done) is True):
				break;
			
		#ȫ������
		if(int(cur_price) <= int(all_sell_condition_price) and int(hold_total) > 0):
			print(("��Ʊ:%s��ǰ�۸�%0.3f����ȫ����������") % (stock_code, (float(cur_price)) / 1000))
			print(("����һ�۸�%0.3fȫ������%d��\r\n") % ((float(buy_price_one))/1000, int(hold_total)))
			futu_comom_api.place_order(socket_to_futu_api, 1, 1, 0, buy_price_one, hold_total, stock_code)
			break
		
		#��ѯ
		time.sleep(1)
	futu_comom_api.disconnect(socket_to_futu_api)	

raw_input("��������˳�")


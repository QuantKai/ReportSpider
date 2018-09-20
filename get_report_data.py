# -*- coding:utf-8 -*-
__author__ = 'kaI'
import os
import sys
import datetime
import pandas as pd
import urllib2
import urllib
import random
import json
import threading

reload(sys)
sys.setdefaultencoding('utf-8')
data_path = 'data'
all_a_stock_df = pd.read_excel('all_A_stock.xls', index_col=0)
if not os.path.exists(data_path):
    os.mkdir(data_path)

# 标识
ur_list = [
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) '
    'AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) '
    'AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'
]


def download_data(stock, num=50):
    if '.'in stock:
        stock = stock.split('.')[0]
    user_agent = random.choice(ur_list)
    request = urllib2.Request('http://data.eastmoney.com/notices/getdata.ashx?StockCode=' + stock +
                              '&CodeType=1&PageIndex=1&PageSize=' + str(num) +
                              '&jsObj=SyKoXofX&SecNodeType=0&FirstNodeType=0&rt=51241203')
    request.add_header('User_Agent', user_agent)
    # 获取
    html = urllib2.urlopen(request)
    data_dict = json.loads(html.read().decode('gbk').split('= ')[1][:-1])
    if os.path.exists(os.path.join(data_path, stock+'.xls')):
        save_df = pd.read_excel(os.path.join(data_path, stock+'.xls'), index_col=0)
    else:
        save_df = pd.DataFrame()
    for data in data_dict['data']:
        if data['INFOCODE'] in save_df.index:
            print data['NOTICETITLE']
            continue
        save_df = save_df.append(pd.DataFrame({'NOTICETITLE': data['NOTICETITLE'],
                                               'EUTIME': data['EUTIME'],
                                               'ANN_RELCOLUMNS': data['ANN_RELCOLUMNS'][0]['COLUMNNAME'],
                                               'Url': data['Url']
                                               }, index=[data['INFOCODE']]))
    save_df['EUTIME'] = pd.to_datetime(save_df['EUTIME'])
    save_df['EUTIME'] = [str(i+datetime.timedelta(days=1))[0:10] for i in save_df['EUTIME']]
    save_df.to_excel(os.path.join(data_path, stock+'.xls'))


def travel_stocks(stocks_list):
    for stock in stocks_list:
        download_data(stock, 50)


def start_spider():
    t_num = 3
    threads = []
    all_a_stock = all_a_stock_df.index.tolist()
    for i in range(t_num):
        if i == t_num-1:
            arg = all_a_stock[(i+1)*1000:len(all_a_stock)]
        else:
            arg = all_a_stock[i*1000:(i+1)*1000]
        print arg
        len(arg)
        t = threading.Thread(target=travel_stocks, args=[arg])
        t.start()
        threads.append(t)
start_spider()


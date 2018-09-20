# -*- coding:utf-8 -*-
__author__ = 'kaI'
import os
import sys
my_path = os.getcwd()
sys.path.append('D:\\kaI\\')
from tool_kai import *
kai = ToolKai(back_test_data=False)
os.chdir(my_path)
import datetime
import pandas as pd
import urllib2
import random
import json
import time
import threading

reload(sys)
sys.setdefaultencoding('utf-8')


class ReportSpider(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = 'date_report_data'
        self.report_df_dict = {}
        # 新建变量用来储存截取剩下的公告
        self.ur_list = [
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) '
            'AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
            'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) '
            'AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'
        ]
        self.main()

    def main(self):
        index = 1
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        os.remove(os.path.join(self.data_path, now_date+'.xls'))
        lack_date = self.check_date()
        if now_date not in lack_date:
            lack_date.append(now_date)
        if len(lack_date) == 1:
            print u'数据已齐全,只爬取当日数据'
        print u'缺少日期序列：'+str(lack_date)
        lack_date.sort()
        data_df_list = []
        while True:
            print u'下载第'+str(index)+u'页数据'
            # noinspection PyBroadException
            try:
                data_df = self.download_data(index)
            except:
                continue
            data_df_list.append(data_df)
            index += 1
            if data_df_list[-1].ix[-1, 'DATE'] < lack_date[0]:
                print u'已下载完'+lack_date[0]+u'之后数据'
                break
            time.sleep(5)
        save_df = pd.DataFrame()
        print u'准备拼合数据'
        for data_df in data_df_list:
            save_df = save_df.append(data_df)
        print u'保存为日期格式'
        for date in lack_date:
            print u'保存日期'+date
            date_df = save_df[save_df['DATE'] == date]
            date_df.to_excel(os.path.join(self.data_path, date+'.xls'))

    def check_date(self):
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)
        date_list = os.listdir(self.data_path)
        date_list = [date.decode('gbk').split('.')[0] for date in date_list]
        all_days_list = kai.tdays_df[kai.tdays_df['alldays'] == 1].loc[self.start_date:self.end_date].index.tolist()
        lack_date = list(set(all_days_list).difference(set(date_list)))
        return lack_date

    def download_data(self, index):
        user_agent = random.choice(self.ur_list)
        request = urllib2.Request('http://data.eastmoney.com/notices/getdata.ashx?StockCode=&'
                                  'FirstNodeType=0&CodeType=1&PageIndex='+str(index) +
                                  '&PageSize=1000&jsObj=AYBAHbzm&'
                                  'SecNodeType=0&Time=&rt=51244570')
        request.add_header('User_Agent', user_agent)
        # 获取
        html = urllib2.urlopen(request)
        data_dict = json.loads(html.read().decode('gbk').split('= ')[1][:-1])
        save_df = pd.DataFrame()
        for data in data_dict['data']:
            if data['INFOCODE'] in save_df.index:
                print data['NOTICETITLE']
                continue
            save_df = save_df.append(pd.DataFrame({'NOTICETITLE': data['NOTICETITLE'],
                                                   'STOCK': data['CDSY_SECUCODES'][0]['SECURITYCODE'],
                                                   'SEC_NAME': data['CDSY_SECUCODES'][0]['SECURITYSHORTNAME'],
                                                   'EUTIME': data['EUTIME'],
                                                   'ANN_RELCOLUMNS': data['ANN_RELCOLUMNS'][0]['COLUMNNAME'],
                                                   'URL': data['Url']
                                                   }, index=[data['INFOCODE']]))
        save_df['EUTIME'] = pd.to_datetime(save_df['EUTIME'])
        save_df['EUTIME'] = [str(i+datetime.timedelta(hours=8)) for i in save_df['EUTIME']]
        save_df['DATE'] = [i[:10] for i in save_df['EUTIME']]
        return save_df

a = ReportSpider('2018-09-01', '2018-09-20')

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


class AnalysisReport(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

        pass

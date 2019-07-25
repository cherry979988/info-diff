# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 13:43:38 2018

@author: xzzz
"""

import xlrd

def get_bid(path_name,count_start,count_end):
    book_rd = xlrd.open_workbook(path_name)
    sheet = book_rd.sheet_by_index(0)
    bid_list = []
    for k in range(count_start-1, count_end):
        string = sheet.cell(k,0).value;
        bid_list.append(string.replace('M_', ''))
    return bid_list

def get_bid_csv(df):
    return df['weiboID'].tolist()
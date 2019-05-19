# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 09:56:18 2018

@author: xzzz
"""

import xlwt
import xlrd
from xlutils.copy import copy

xls_all = xlrd.open_workbook(r'attitude_all.xls')
sheets_number = xls_all.nsheets
sheet0 = xls_all.sheet_by_index(sheets_number-1)
now_rows = sheet0.nrows

xls = xlrd.open_workbook(r'attitude.xls')
sheet_wr = xls.sheet_by_index(0)
col_num = sheet_wr.ncols
row_num = sheet_wr.nrows - 1

rb = xlrd.open_workbook(r'attitude_all.xls', formatting_info=True)
wb = copy(rb)
ws = wb.get_sheet(0)
ws.write(0,0,'aaaa')
wb.save(r'other.xls')




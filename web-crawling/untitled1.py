# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 21:54:10 2018

@author: xzzz
"""

import xlwt

book_wr = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book_wr.add_sheet('test',cell_overwrite_ok=True)
col = 0
row = 0
sheet.write(row, col, '微博ID')
col += 1
sheet.write(row, col, '用户ID')
col += 1
sheet.write(row, col, '用户名')
col += 1
sheet.write(row, col, '微博内容')
col += 1
sheet.write(row, col, '时间')
col += 1
sheet.write(row, col, '转发数')
col += 1
sheet.write(row, col, '赞数')
col += 1
sheet.write(row, col, '评论数')
col = 0
row += 1

book_wr.save(r'content3.xls')
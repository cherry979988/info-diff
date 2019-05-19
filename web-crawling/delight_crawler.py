# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 15:16:38 2018

@author: xzzz
"""

import requests
import time
import xlwt
import re
from bs4 import BeautifulSoup
import gc
import read_bid
book_wr = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book_wr.add_sheet('test',cell_overwrite_ok=True)

row = 0
col = 0
sheet.write(row, col, '用户名')
col += 1
sheet.write(row, col, '用户名id')
col += 1
sheet.write(row, col, '时间')
row += 1
col = 0
book_wr.save(r'attitude.xls')

#pre_url = 'https://weibo.cn/attitude/G41yqqTyi?rl=1&page='

headers =  {
        'cookie':'SCF=AuilS8C_l_Q4hcWzAntCupw6ySHu1JGSv06YfW1Q01YbXFuKIDQ-AbyRk_q7hteQzIb07nK0gJtceZM9F-G_aB4.; _T_WM=3e357b698836f1d3b5c126c4bf9138fc; SUB=_2A252S4HwDeRhGeBL61cS8S_Nyj-IHXVVty-4rDV6PUJbkdBeLW6kkW1NR06S8mnW27rUMebk6dSAlGJF-6SmrL7N; SUHB=0d4-eYtAjaj-SH',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }

count = 61270



#bid = ['G41pGh8LI','G4bQKjSVz','G41oXiQIi','G46KS1owP','G42h8v9mg','G47a33K52','G423pbcaN','G41pS2uDe','G41BfE77C','G49eM0vPN','G4aLIbEzr','G41BppoWc','G41QC4W6p','G3XA1fBTI','G4uBpzOVh','G3WFTtTyN','G49rF0OTB']

#'G4uy99S0t','G426NybQw','G41LbxlOz','G46YHfcM8','G430Nj8J1','G40sQ64zZ','G3WLZseST','G46rojy34','G46zx2DB4','G42kw2N8c',
bid = read_bid.get_bid('content2.xls',248,294)
for blog_name in bid:
    pre_url = 'https://weibo.cn/attitude/' + blog_name + '?rl=1&page='
    url = pre_url + str(1)
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    page_tag = soup.find('input', attrs={'name':'mp', 'type':'hidden'})
    if page_tag is None:
        page_number = 1
    else:
        page_number = int(page_tag.attrs['value'])
    del url,r,soup, page_tag
    gc.collect()
    time.sleep(8)
    while count <= page_number:
        url = pre_url + str(count)
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        mark_tag = soup.find('div', attrs={'id':'attitude'})
#       如果发生微博官方不予给出数据的情况，强行暂停一分钟之后再对原界面重新进行请求
        while mark_tag is None:
            del r, soup, mark_tag
            gc.collect()
            time.sleep(80)
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')
            mark_tag = soup.find('div', attrs={'id':'attitude'})
        d_list = mark_tag.find_all_next('div', attrs={'class':'c'})
        d_list_len = len(d_list)
        for j in range(d_list_len):
            uname = d_list[j].a.text
            sheet.write(row, col, uname)
            col += 1
            result = re.search(r'/(\d+)$',d_list[j].a.attrs['href'])
            if not result is None:
                sheet.write(row, col, result.group(1))
            col += 1
            sheet.write(row, col, d_list[j].span.text)
            row += 1
            col = 0
            del uname, result
            gc.collect()
        book_wr.save(r'attitude.xls')
        print('tweet_id '+blog_name+' '+'page '+str(count)+' has done')
        del url, r, soup, mark_tag, d_list
        count += 1
        time.sleep(3)
    count = 1
    
    




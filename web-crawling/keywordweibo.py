# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 10:20:16 2018

@author: xzzz, yeqy15
"""
  
import requests
from bs4 import BeautifulSoup
import re
import gc
import time
import pandas as pd
import os
import argparse
from utils import getTime

parser = argparse.ArgumentParser()
parser.add_argument('--save_dir', type=str, default='./data')
parser.add_argument('--keyword', type=str, default='重庆公交车')
parser.add_argument('--start_time', type=str, default='20181101')
parser.add_argument('--end_time', type=str, default='20181110')
parser.add_argument('--end_page', type=int, default=20)
args = parser.parse_args()
opt = vars(args)

def info_separate(tweet):
    bid = tweet.attrs['id']
    child_list = tweet.find_all(name='div')
#    每一条微博标签下只可能有两个div标签（有图）和一个div标签（无图）两种情况
    child_list_length = len(child_list)
    if child_list_length == 1:
        atag = child_list[0].a
        uname = atag.text
        uidstr = atag.attrs['href']
        uid = re.search(r'/(\w+)$',uidstr).group(1)
        cont_str = child_list[0].text
        try:
            d_num = re.search(r'赞\[(\d+)\]',cont_str).group(1)
            r_num = re.search(r'转发\[(\d+)\]',cont_str).group(1)
            c_num = re.search(r'评论\[(\d+)\]',cont_str).group(1)

            d_str = re.search(r'赞\[(\d+)\]', cont_str).group(0)
            en = cont_str.find(d_str)
            st = cont_str.find(':')
            cont = cont_str[st+1:en].strip(' ').replace(';', ' ')

            time = getTime(cont_str)
        except:
            print(cont_str)
            time, d_num, r_num, c_num = 0, 0, 0, 0
        return bid,uid,uname,cont,time,d_num,r_num,c_num
    else:
        uname = child_list[0].a.text
        uidstr = child_list[0].a.attrs['href']
        uid = re.search(r'/(\w+)$',uidstr).group(1)

        cont = child_list[0].text
        st = cont.find(':')
        cont = cont[st+1:].strip(' ').replace(';', ' ')

        cont_str = child_list[1].text
        d_num = re.search(r'赞\[(\d+)\]',cont_str).group(1)
        r_num = re.search(r'转发\[(\d+)\]',cont_str).group(1)
        c_num = re.search(r'评论\[(\d+)\]',cont_str).group(1)
        time = getTime(cont_str)
        return bid,uid,uname,cont,time,d_num,r_num,c_num


heads = ['weiboID', 'userID', 'username', 'content', 'timestamp', 'n_repost', 'n_delight', 'n_comment']
df = pd.DataFrame(columns=heads)
row = 0
    
#爬取weibo.cn的界面，使用其提供的搜索引擎作为
url = 'https://weibo.cn/search/'

#请求头，最重要的是cookie和user-agent
headers = {
        'cookie':'SUB=_2A25xd-3rDeRhGeNL41QY8SbKyzSIHXVSm_OjrDV6PUJbkdAKLWnskW1NSMfRlWPnS0UmLr6msd747BJetmmokRFp; SUHB=0mxUN7tzuc3IHy; SCF=Ajf8CFaYdZ-Vtwe9DZrML1aiYTQnrCDVaSROMCXLSlG-cLs513iMHMPKQ-70gnpIDjc6kUVk0er1leJUaBcSmLk.; _T_WM=ea07026bc9a35c211e276d137dc7c3f6',
        'user-agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
        }

#请求参数，其意义分别是启用高级搜索，关键词，是否原创，起始时间，结束时间，排序方式热门，页数控制
#特别的改变参数page的大小就可以得到每一页搜索的源代码
payload = {
        'advancedfilter':'1',
        'keyword':opt['keyword'],
        'hasori':'1',
    	'haslink':'1',
        'starttime':opt['start_time'],
        'endtime':opt['end_time'],
        'sort':'time',
        'smblog':'搜索',
        'page':1
        }

save_dir_full = os.path.join(opt['save_dir'], opt['keyword'])
if not os.path.exists(save_dir_full):
    os.makedirs(save_dir_full)

for k in range(1, opt['end_page'] + 1):
    #利用post方法请求页面得到每一个页面的源代码
    payload['page'] = k
    r = requests.post(url, headers=headers, data=payload)
    html = r.content
    #使用beautifulsoup对页面加以解析
    soup = BeautifulSoup(html, 'html5lib')
    tweet_list = soup.find_all(name='div', attrs={'class':'c', 'id':True})
    for tweet in tweet_list:
        bid,uid,uname,cont,btime,d_num,r_num,c_num = info_separate(tweet)
        df.loc[row]=[bid, uid, uname, cont, btime, d_num, r_num, c_num]
        row += 1
        del bid,uid,uname,cont,btime,d_num,r_num,c_num
        gc.collect()
    df.to_csv(os.path.join(save_dir_full, 'content.csv'), index=False)
    del tweet_list, soup, html, r
    gc.collect()
    time.sleep(3)
    print('page '+str(k)+' has done')

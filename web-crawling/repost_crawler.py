# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 15:16:15 2018

@author: xzzz
"""

import requests
from bs4 import BeautifulSoup
import os
import re
import gc
import time
import read_bid
import pandas as pd
import argparse
import pickle
from utils import getTime, getCleanRepostText

parser = argparse.ArgumentParser()
parser.add_argument('--save_dir', type=str, default='./data')
parser.add_argument('--keyword', type=str, default='重庆公交车')
parser.add_argument('--comment', type=bool, default=False)
args = parser.parse_args()
opt = vars(args)

if opt['comment']:
    interactionType = 'comment'
else:
    interactionType = 'repost'

heads = ['weiboID', 'username', 'userID', 'content', 'n_delight', 'time', 'previous_username']

headers = {
        'cookie':'MLOGIN=0; _T_WM=428754f866651a74ed953b4924a39363; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D102803; SUB=_2A25xd-3rDeRhGeNL41QY8SbKyzSIHXVSm_OjrDV6PUJbkdAKLWnskW1NSMfRlWPnS0UmLr6msd747BJetmmokRFp; SUHB=0mxUN7tzuc3IHy; SCF=Ajf8CFaYdZ-Vtwe9DZrML1aiYTQnrCDVaSROMCXLSlG-cLs513iMHMPKQ-70gnpIDjc6kUVk0er1leJUaBcSmLk.; SSOLoginState=1551080891',
        'user-agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
}

df0 = pd.read_csv(os.path.join(opt['save_dir'], opt['keyword'], 'content.csv'))
bid_list = read_bid.get_bid_csv(df0)

save_dir_full = os.path.join(opt['save_dir'], opt['keyword'], interactionType)
if not os.path.exists(save_dir_full):
    os.makedirs(save_dir_full)

progress_dir = os.path.join(save_dir_full, 'progress.pkl')
if not os.path.exists(progress_dir):
    done_list = []
else:
    progress_file = open(progress_dir, 'rb')
    done_list = pickle.load(progress_file)
    progress_file.close()

count = 1
for bid in bid_list:

    if bid in done_list:
        continue

    row = 0
    df = pd.DataFrame(columns=heads)

    pre_url =  'https://weibo.cn/%s/' % interactionType +bid[2:]+'?rl=1&page='
    url = pre_url + str(1)
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    page_tag = soup.find('input',attrs={'name':'mp', 'type':'hidden'})
    if page_tag is None:
        page_all = 1
    else:
        page_all = int(page_tag['value'])
    del url,r,soup,page_tag
    gc.collect
    time.sleep(3)
    while count <= page_all:
        url = pre_url + str(count)
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')
        raw_list = soup.find_all('span', attrs={'class':'ct'})
        if len(raw_list) == 0:
            # 转发不被显示的微博，跳过
            print('Reposts/comments of %s are not shown.' % bid)
            break
        if len(raw_list) != 0:
            tweet_list = []
            for time_tag in raw_list:
                tweet_list.append(time_tag.parent)
            for tweet in tweet_list:
                if 'class' in tweet.attrs.keys():
                    content = tweet.text
                    btime = getTime(content)
                    name_tag = tweet.a
                    uname = name_tag.text
                    uid_string = name_tag.attrs['href']
                    uid = re.search(r'/([\w,?,=]+)$',uid_string).group(1)
                    retweet_list = re.findall(r'//@(.*?)[：,:]',content)
                    retweet_string = ','.join(retweet_list)
                    content_clean, like_n = getCleanRepostText(content, interactionType)
                    df.loc[row]=[bid, uname, uid, content_clean, like_n, btime, retweet_string]
                    row += 1
                    del retweet_list, uid, uid_string, uname, name_tag, btime, content, content_clean, like_n
                    gc.collect
        
            del tweet_list
            gc.collect
        print('blog '+bid+' '+ 'page '+ str(count) + ' has done')
        df.to_csv(os.path.join(opt['save_dir'], opt['keyword'], interactionType, bid + '.csv'), index=False)
        count += 1
        del raw_list, soup, r, url
        time.sleep(3)
    count = 1
    done_list.append(bid)
    progress_file = open(progress_dir, 'wb')
    pickle.dump(done_list, progress_file)
    del df
                                                                                                                                                                      
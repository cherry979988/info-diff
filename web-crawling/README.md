This folder contains source code to crawl weibo data.

1. Get cookie and fill in L78 in keywordweibo.py, L34 in repost_crawler.py
You need to visit weibo.cn, log in your own account, get the header from your GET requests.
```
headers = {
        'cookie':'MLOGIN=0; _T_WM=428754f866651a74ed953b4924a39363; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D102803; SUB=_2A25xd-3rDeRhGeNL41QY8SbKyzSIHXVSm_OjrDV6PUJbkdAKLWnskW1NSMfRlWPnS0UmLr6msd747BJetmmokRFp; SUHB=0mxUN7tzuc3IHy; SCF=Ajf8CFaYdZ-Vtwe9DZrML1aiYTQnrCDVaSROMCXLSlG-cLs513iMHMPKQ-70gnpIDjc6kUVk0er1leJUaBcSmLk.; SSOLoginState=1551080891',
        'user-agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
}
```

2. Run keywordweibo.py
```
python3 keywordweibo.py --keyword 巴黎圣母院 --start_time 20190415 --end_time 20190422 --end_page 100
```

By default, the results are saved to a csv file in ./data/*keyword*/

3. Run repost_crawler.py
To crawl repost:
```
python3 repost_crawler.py --keyword 巴黎圣母院
```
By default, the results are saved to a csv file in ./data/*keyword*/repost/

To crawl comments:
```
python3 repost_crawler.py --keyword 巴黎圣母院 --comment True
```
By default, the results are saved to a csv file in ./data/*keyword*/comment
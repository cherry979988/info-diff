import re
from time import strftime, localtime, strptime, mktime

def getTime(cont_str):
    '''微博中可能出现三种格式的时间，统一成为2019-01-10 00:00:00的格式'''
    if cont_str.find('今天'):
        cont_str.replace('今天', strftime('%m月%d日', localtime()))
    # 第一种情形：2019-01-10 00:00:00
    time = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', cont_str)
    if time is None:
        time = re.search(r'\d{2}月\d{2}日\s\d{2}:\d{2}', cont_str)
        if time is None:
            # 其他情形
            time = 'unknown time'
        else:
            # 第二种情形：01月10日 00:00
            struct_time = strptime(time.group(0), "%m月%d日 %H:%M")
            year = localtime().tm_year
            month = struct_time.tm_mon
            day = struct_time.tm_mday
            hour = struct_time.tm_hour
            minute = struct_time.tm_min
            if struct_time > localtime():
                year -= 1
            time = strftime('%Y-%m-%d %H:%M:%S', (year, month, day, hour, minute, 0, 0, 0, 0))
    else:
        time = time.group(0)
    return time

def getCleanRepostText(cont_str, interactionType):
    st = cont_str.find(':')
    en1 = cont_str.find('//@')
    if en1 < 0:
        en1 = len(cont_str)
    re_search = re.search(r'赞\[(\d+)\]', cont_str)
    # key = re_search.group(0)
    like_n = int(re_search.group(1))
    if interactionType == 'comment':
        en2 = cont_str.find('举报')
    else:
        en2 = cont_str.find(re_search.group(0))
    en = min(en1, en2)
    clean_cont = cont_str[st+1:en]
    return clean_cont, like_n
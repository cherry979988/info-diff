import os
import time
import pandas as pd
import sys
from multiprocessing import Process, Lock

PROCESS_COUNT = 6
MAX_WINDOW = 10
MERGED_DIR = '../data/weibo_dataset/retweetWithoutContent/merged_entries'
INSTANCE_DIR = '../data/weibo_dataset/retweetWithoutContent/instances'

columns = ['username', 'seenWeiboIDs', 'seenWeiboUsers', 'decisionWeiboID']

def find_all_location(element, list):
    ret = []
    for i, item in enumerate(list):
        if item == element:
            ret.append(i)
    return ret

def worker(id, filelist):
    print('Thread %d: %s -- %s, Starting... ' % (id, filelist[0], filelist[-1]))
    start_time = time.time()

    for j, file in enumerate(filelist):
        username = file[:-4]

        df1 = pd.read_csv(os.path.join(MERGED_DIR, file))

        df2 = pd.DataFrame(columns=['seenWeiboIDs', 'decisionWeiboID'])

        p = 0
        q = 0
        idx = 0
        n = len(df1)
        instances = []

        while q < n:
            while q < n and df1['type'][q] == 1:
                q += 1
            # instances.append((p, q))
            df2.loc[idx] = [p, q]
            while q < n and df1['type'][q] == 0:
                q += 1
            p = q
            idx += 1

        # instances.append((n, n))
        df2.loc[idx] = [n, n]
        df3 = pd.DataFrame(columns=columns)

        for i in range(len(df2) - 1):
            p = df2['seenWeiboIDs'][i]
            q = df2['decisionWeiboID'][i]
            r = df2['seenWeiboIDs'][i+1]
            df3.loc[i] = [username,
                          '_'.join(map(str, df1['weiboID'][p:q])),
                          '_'.join(map(str, df1['username'][p:q])),
                          '_'.join(map(str, df1['weiboID'][q:r]))]

        # if len(df3) > 0:
        #     df3.to_csv(os.path.join(INSTANCE_DIR, file), index=False)

        df4 = pd.DataFrame(columns=columns)
        idx = 0
        for i in range(len(df2) - 1):
            p = df2['seenWeiboIDs'][i]
            q = df2['decisionWeiboID'][i]
            r = df2['seenWeiboIDs'][i + 1]
            seen = df1['weiboID'][p:q]
            retweet = df1['username'][q:r]
            for item in retweet:
                ret = find_all_location(item, seen)
                for location in ret:
                    df4.loc[idx] = [username,
                                    '_'.join(map(str, df1['weiboID'][max(p, location - MAX_WINDOW):location])),
                                    '_'.join(map(str, df1['username'][max(p, location - MAX_WINDOW):location])),
                                    item]
                    idx += 1

        if len(df4) > 0:
            df4.to_csv(os.path.join(INSTANCE_DIR, file), index=False)

        if j % 10 == 0:
            sys.stdout.write("Process %d, parsed %d users, Time: %d sec\r" % (id, j, time.time() - start_time))
            sys.stdout.flush()

    print('Thread: %s -- %s, Finished' % (filelist[0], filelist[-1]))

def main():
    if not os.path.exists(INSTANCE_DIR):
        os.mkdir(INSTANCE_DIR)

    lst = os.listdir(MERGED_DIR)
    n = len(lst)

    each_proc = int(n / PROCESS_COUNT)
    print('%d users in total, %s users in each thread.' % (n, each_proc))

    procs = []
    for i in range(PROCESS_COUNT - 1):
        p = Process(target=worker, args=(i+1, lst[i*each_proc:(i+1) * each_proc]))
        p.start()
        procs.append(p)

    p = Process(target=worker, args=(PROCESS_COUNT, lst[(PROCESS_COUNT-1) * each_proc:]))
    p.start()
    procs.append(p)

    for proc in procs:
        proc.join()

if __name__ == "__main__":
    main()

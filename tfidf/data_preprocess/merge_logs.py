import os
import time
import pandas as pd
import sys
from multiprocessing import Process, Lock

PROCESS_COUNT = 6
RETWEET_DIR = '../data/weibo_dataset/retweetWithoutContent/retweet_entries'
SEEN_DIR = '../data/weibo_dataset/retweetWithoutContent/seen_entries'
MERGED_DIR = '../data/weibo_dataset/retweetWithoutContent/merged_entries'

START_TIME = '2012-07-01-00:00:00'
END_TIME = '2012-08-01-00:00:00'

columns = ['username', 'weiboID', 'timestamp', 'info', 'type']

def worker(id, filelist):
    print('Thread %d: %s -- %s, Starting... ' % (id, filelist[0], filelist[-1]))
    start_time = time.time()

    for i, file in enumerate(filelist):

        # retweet
        df1 = pd.read_csv(os.path.join(RETWEET_DIR, file))
        df1.insert(loc=3, column='type', value=[0] * len(df1))

        # seen
        df2 = pd.read_csv(os.path.join(SEEN_DIR, file))
        df2.insert(loc=3, column='type', value=[1] * len(df2))
        df2.drop(columns=['Unnamed: 0'], inplace=True)

        df = df1.append(df2, sort=False)
        df = df.sort_values(by=['timestamp'])

        df = df[(df['timestamp'] > START_TIME) & (df['timestamp'] < END_TIME)]
        df.to_csv(os.path.join(MERGED_DIR, file), index=False)

        if i % 10 == 0:
            sys.stdout.write("Process %d, parsed %d users, Time: %d sec\r" % (id, i, time.time() - start_time))
            sys.stdout.flush()

    print('Thread: %s -- %s, Finished' % (filelist[0], filelist[-1]))

def main():
    if not os.path.exists(MERGED_DIR):
        os.mkdir(MERGED_DIR)

    lst = os.listdir(SEEN_DIR)
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

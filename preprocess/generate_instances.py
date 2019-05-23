import argparse
import pandas as pd
import time
import os
import sys
import random
from multiprocessing import Process

parser = argparse.ArgumentParser()
parser.add_argument('--window_size', type=int, default=10)
parser.add_argument('--n_process', type=int, default=12)
parser.add_argument('--input_dir', type=str, default='./data/merged_entries')
parser.add_argument('--output_dir', type=str, default='./data/instancesnew')
parser.add_argument('--output_merged_dir', type=str, default='./data/instancesnewm')
parser.add_argument('--negative_ratio', type=int, default=5)

args = parser.parse_args()
opt = vars(args)

columns = ['username', 'seenWeiboIDs', 'seenWeiboUsers', 'decisionWeiboID', 'label']

def find_all_location(element, list):
    ret = []
    for i, item in enumerate(list):
        if item == element:
            ret.append(i)
    return ret

def worker(id, filelist):
    print('Thread %d: %s -- %s, Starting... ' % (id, filelist[0], filelist[-1]))
    start_time = time.time()

    invalid = 0
    filename_all = os.path.join(opt['output_merged_dir'], 'worker%d.csv' % id)
    df_all = pd.DataFrame(columns=columns)
    df_all.to_csv(filename_all, index=False)

    for j, file in enumerate(filelist):

        if j % 10 == 0:
            sys.stdout.write("Process %d, parsed %d users (%d are invalid), Time: %d sec\r" % (id, j, invalid, time.time() - start_time))
            sys.stdout.flush()

        if os.path.exists(os.path.join(opt['output_dir'], file)):
            continue

        username = file[:-4]

        df1 = pd.read_csv(os.path.join(opt['input_dir'], file))

        df2 = pd.DataFrame(columns=['seenWeiboIDs', 'decisionWeiboID'])

        p = 0
        q = 0
        idx = 0
        n = len(df1)

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
        # df3 = pd.DataFrame(columns=columns)
        #
        # for i in range(len(df2) - 1):
        #     p = df2['seenWeiboIDs'][i]
        #     q = df2['decisionWeiboID'][i]
        #     r = df2['seenWeiboIDs'][i+1]
        #     df3.loc[i] = [username,
        #                   '_'.join(map(str, df1['weiboID'][p:q])),
        #                   '_'.join(map(str, df1['username'][p:q])),
        #                   '_'.join(map(str, df1['weiboID'][q:r]))]

        # if len(df3) > 0:
        #     df3.to_csv(os.path.join(INSTANCE_DIR, file), index=False)
        if idx < 2:
            invalid += 1
            continue

        df4 = pd.DataFrame(columns=columns)
        idx = 0

        for i in range(len(df2) - 1):
            p = df2['seenWeiboIDs'][i]
            q = df2['decisionWeiboID'][i]
            r = df2['seenWeiboIDs'][i + 1]
            seen = df1['weiboID'][p:q]
            retweet = df1['weiboID'][q:r]
            for item in retweet:
                ret = find_all_location(item, seen)
                for location in ret:
                    df4.loc[idx] = [username,
                                    '_'.join(map(str, df1['weiboID'][p + location: min(p + location + opt['window_size'], q)].iloc[::-1])),
                                    '_'.join(map(str, df1['username'][p + location: min(p + location + opt['window_size'], q)].iloc[::-1])),
                                    item,
                                    1]
                    idx += 1
                    for k in range(opt['negative_ratio']):
                        rnd = random.randint(p, q - 1)
                        cnt = 0
                        while rnd - p in ret:
                            rnd = random.randint(p, q - 1)
                            cnt += 1  # 防止死循环
                            if cnt > 5:
                                break
                        item0 = df1['weiboID'][rnd]
                        df4.loc[idx] = [username,
                                        '_'.join(map(str, df1['weiboID'][rnd: min(q, rnd + opt['window_size'])].iloc[::-1])),
                                        '_'.join(map(str, df1['username'][rnd: min(q, rnd + opt['window_size'])].iloc[::-1])),
                                        item0,
                                        0]
                        idx += 1

        if len(df4) > 0:
            df4.to_csv(os.path.join(opt['output_dir'], file), index=False)
            df4.to_csv(filename_all, index=False, header=False, mode='a+')

            # df_all = df_all.append(df4)
            #
            # if j % 10 == 0:
            #     df_all.to_csv(filename_all, index=False)

    print('Thread: %s -- %s, Finished' % (filelist[0], filelist[-1]))

def merge_all():
    filename_all = os.path.join(opt['output_merged_dir'], 'all.csv')
    pd.DataFrame(columns=columns).to_csv(filename_all, index=False)
    for i in range(1, opt['n_process'] + 1):
        df = pd.read_csv(os.path.join(opt['output_merged_dir'], 'worker%d.csv' % i))
        df.to_csv(filename_all, index=False, header=False, mode='a+')

    print('csv file of %d workers are merged in %s.' % (opt['n_process'], opt['output_merged_dir']))


def main(opt):
    if not os.path.exists(opt['output_dir']):
        os.mkdir(opt['output_dir'])

    if not os.path.exists(opt['output_merged_dir']):
        os.mkdir(opt['output_merged_dir'])

    lst = os.listdir(opt['input_dir'])
    n = len(lst)

    each_proc = int(n / opt['n_process'])
    print('%d users in total, %s users in each thread.' % (n, each_proc))

    procs = []
    for i in range(opt['n_process'] - 1):
        p = Process(target=worker, args=(i+1, lst[i*each_proc:(i+1) * each_proc]))
        p.start()
        procs.append(p)

    p = Process(target=worker, args=(opt['n_process'], lst[(opt['n_process'] - 1) * each_proc:]))
    p.start()
    procs.append(p)

    for proc in procs:
        proc.join()

    merge_all()

if __name__ == '__main__':
    main(opt)
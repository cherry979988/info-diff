import os
import pandas as pd
import linecache
from multiprocessing import Process, Lock
import sys
import time
import shutil

PROCESS_COUNT = 6
FILENAME = '../data/weibo_dataset/weibo_network.txt'
RETWEET_DIR = '../data/weibo_dataset/retweetWithoutContent/retweet_entries'
SEEN_DIR = '../data/weibo_dataset/retweetWithoutContent/seen_entries'
PROGRESS_DIR = '../data/weibo_dataset/retweetWithoutContent/progress_log'
columns = ['username', 'weiboID', 'timestamp', 'info']


def get_followees(userId):
    line = linecache.getline(FILENAME, userId + 2)
    ele = line.strip().split('\t')
    newUserId = int(ele[0])
    assert(userId == newUserId)
    # n_follower = ele[1]
    followee_list = [ele[i] for i in range(2, len(ele), 2)]
    return followee_list
# count = linecache.getline(filename,linenum)

def worker(id, filelist, lock, start_idx=0, time_passed=0):
    print('Thread %d: %s -- %s, Starting... ' % (id, filelist[0], filelist[-1]))
    start_time = time.time()

    for i, file in enumerate(filelist):
        # for small-scale testing
        # if i > 10:
        #     break
        if i < start_idx:
            continue

        userId = int(file[:-4]) # '.csv' is removed

        filename = os.path.join(SEEN_DIR, file)
        df = pd.DataFrame(columns=columns)

        followees = get_followees(userId)

        for followee in followees:
            filename_followee = os.path.join(RETWEET_DIR, followee + '.csv')

            # if this followee hasn't tweeted anything, just go on
            if not os.path.isfile(filename_followee):
                continue

            df2 = pd.read_csv(filename_followee)
            df = df.append(df2)

        #lock.acquire()
        df.to_csv(filename)
        #lock.release()
        if i % 10 == 0:
            sys.stdout.write("Process %d, parsed %d users, Time: %d sec\r" % (id, i, time.time() - start_time + time_passed))
            sys.stdout.flush()
            log_progress(id, i, time.time() - start_time + time_passed)

    print('Thread: %s -- %s, Finished' % (filelist[0], filelist[-1]))

def load_progress():
    ret = []
    for i in range(PROCESS_COUNT):
        filename = os.path.join(PROGRESS_DIR, 'p%d.txt' % i)
        if os.path.isfile(filename):
            file = open(filename, 'r')
            line = file.readline().strip().split(' ')
            # parsed = line[0]
            # time = line[1]
            ret.append([int(line[0]), int(line[1])])
        else:
            ret.append([0, 0])
    return ret

def log_progress(id, idx, time):
    filename = os.path.join(PROGRESS_DIR, 'p%d.txt' % id)
    file = open(filename, 'w')
    file.write('%d %d\n' % (idx, time))
    file.close()

def main():
    if not os.path.exists(SEEN_DIR):
        os.mkdir(SEEN_DIR)

    if not os.path.exists(PROGRESS_DIR):
        os.mkdir(PROGRESS_DIR)

    progress = load_progress()

    lst = os.listdir(RETWEET_DIR)
    n = len(lst)

    each_proc = int(n / PROCESS_COUNT)
    print('%d users in total, %s users in each thread.' % (n, each_proc))
    lock = Lock()
    procs = []
    for i in range(PROCESS_COUNT - 1):
        p = Process(target=worker, args=(i+1, lst[i*each_proc:(i+1) * each_proc],
                                         lock, progress[i][0], progress[i][1]))
        p.start()
        procs.append(p)

    p = Process(target=worker, args=(PROCESS_COUNT, lst[(PROCESS_COUNT-1) * each_proc:],
                                     lock, progress[PROCESS_COUNT-1][0], progress[PROCESS_COUNT-1][1]))
    p.start()
    procs.append(p)

    for proc in procs:
        proc.join()

if __name__ == '__main__':
    main()
import pandas as pd
import linecache
from multiprocessing import Process, Lock

# count = linecache.getline(filename,linenum)
PROCESS_COUNT = 5
FILENAME = '../data/weibo_dataset/weibo_network.txt'
def worker(start, end, lock):
    print(start, end)
    df = pd.DataFrame(columns=['userID', 'n_follower', 'follower_list'])
    idx = 0
    for i in range(start, end):
        line = linecache.getline(FILENAME, i+2)
        ele = line.strip().split('\t')
        userID = ele[0]
        n_follower = ele[1]
        follower_list = ','.join([ele[i] for i in range(2,len(ele),2)])
        df.loc[idx] = [userID, n_follower, follower_list]
        idx += 1

    csv_name = str(start) + '_' + str(end)
    df.to_csv('../data/weibo_dataset/follower_network/%s' % csv_name, index=False)

def main():
    file = open(FILENAME, 'r')
    ele = file.readline().strip().split('\t')
    n = int(ele[0])

    each_proc = int(n/PROCESS_COUNT)
    lock = Lock()
    procs = []
    for i in range(PROCESS_COUNT - 1):
        p = Process(target=worker, args=(i*each_proc, (i+1) * each_proc, lock))
        p.start()
        procs.append(p)

    p = Process(target=worker, args=((PROCESS_COUNT-1) * each_proc, n+1, lock))
    p.start()
    procs.append(p)

    for proc in procs:
        proc.join()

if __name__ == '__main__':
    main()
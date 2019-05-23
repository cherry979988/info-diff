import os
import pickle
import linecache
import argparse
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('--filename', type=str, default='../data/weibo_dataset/weibo_network.txt')
parser.add_argument('--output', type=str, default='../data/weibo_dataset/followee_count.pkl')

args = parser.parse_args()
opt = vars(args)

def get_followees(filename, userId):
    line = linecache.getline(filename, userId + 2)
    ele = line.strip().split('\t')
    newUserId = int(ele[0])
    assert(userId == newUserId)
    # n_followee = int(ele[1])
    return int(ele[1])

def main(opt):
    filename = opt['filename']
    line = linecache.getline(filename, 1)
    n_users = int(line.split('\t')[0])
    print('#users: {}'.format(n_users))
    followee_dict = {}
    start_time = time.time()
    for i in range(n_users):
        followee_dict[i] = get_followees(filename, i)
        if i % 100 == 0:
            sys.stdout.write("Parsed %d users, Time: %d sec\r" % (i, time.time() - start_time))
            sys.stdout.flush()

    # followee_dict = {i: get_followees(filename, i) for i in range(n_users)}
    pickle.dump(followee_dict, open(opt['output'], 'wb'))

if __name__ == '__main__':
    main(opt)
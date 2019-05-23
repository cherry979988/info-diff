import pandas as pd
import pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, default='./data/final/train.csv')
parser.add_argument('--output', type=str, default='./data/final/idx_dict.pkl')
args = parser.parse_args()

opt = vars(args)
print(opt)

def get_allWeiboIDs(df):
    allWeiboIDs = set()
    for seen in df['seenWeiboIDs']:
        if len(seen) > 0:
            allWeiboIDs.update(list(map(int, seen.split('_'))))
    return allWeiboIDs

df = pd.read_csv(opt['input'])
allWeiboIDs = get_allWeiboIDs(df)
weibo2embid = {v: k + 1 for k, v in enumerate(allWeiboIDs)}

with open(opt['output'], 'wb') as fout:
    pickle.dump(weibo2embid, fout)
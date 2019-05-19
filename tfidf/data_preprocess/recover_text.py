import os
import pickle
import pandas as pd

FILENAME = '../data/weibo_dataset/Root_Content.csv'
DICT_SAVE = '../data/weibo_dataset/weibocontents/dict.pkl'

def main():
    df = pd.read_csv(FILENAME)

    df['']



    file = open(DICT_SAVE, 'wb')
    pickle.dump({'word2idx': word2idx, 'idx2word':idx2word}, file)


if __name__ == '__main__':
    main()
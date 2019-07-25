import os
import pickle

FILENAME = '../data/weibo_dataset/weibocontents/WordTable.txt'
DICT_SAVE = '../data/weibo_dataset/weibocontents/dict.pkl'

def main():
    pass
    with open(FILENAME, 'r', encoding='gb18030') as f:
        line = f.readline()
        n = int(line)

        word2idx = {}
        idx2word = {}

        while True:
            try:
                line = f.readline().strip().split('\t')
                word2idx[line[2]] = line[0]
                idx2word[line[0]] = line[2]

            except:
                print('End of file...')
                break

    file = open(DICT_SAVE, 'wb')
    pickle.dump({'word2idx': word2idx, 'idx2word':idx2word}, file)


if __name__ == '__main__':
    main()
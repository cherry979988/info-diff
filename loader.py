import json
import random
import torch
import numpy as np
import pandas as pd

from utils import constant
from utils.project_utils import safe_retrieve
import pickle

class DataLoader(object):
    def __init__(self, filename, batch_size, opt, weibo2embid=None, evaluation=False):
        self.batch_size = batch_size
        self.opt = opt
        self.eval = evaluation

        self.followee_count = pickle.load(open(opt['followee_count_file'], 'rb'))

        # with open(filename) as infile:
        df = pd.read_csv(filename).fillna('')

        self.allWeiboIDs = set()
        self.get_allWeiboIDs(df)
        if weibo2embid is None:
            self.weibo2embid = {v: k + 1 for k, v in enumerate(self.allWeiboIDs)}
        else:
            self.weibo2embid = weibo2embid

        data = self.preprocess(df, opt)

        if not evaluation:
            indices = list(range(len(data)))
            random.shuffle(indices)
            data = [data[i] for i in indices]

        self.labels = [d[-1] for d in data]

        data = [data[i:i+batch_size] for i in range(0, len(data), batch_size)]
        self.data = data
        self.num_examples = len(data)
        print("{} batches created for {}".format(len(data), filename))


    # leave idx 0 for unknown

    def preprocess(self, data, opt):
        processed = []

        n_users = len(self.followee_count)
        seen_count = {}
        retw_count = {}

        for i in range(len(data)):
            if data['seenWeiboIDs'][i] == '':
                continue

            user = int(data['username'][i])

            seqlen = len(data['seenWeiboIDs'][i])
            seen = map_emb_index(data['seenWeiboIDs'][i], self.weibo2embid)[:min(opt['window_size'], seqlen)]

            seen_users = list(map(int, data['seenWeiboUsers'][i].split('_')))[:min(opt['window_size'], seqlen)]

            decision = safe_retrieve(self.weibo2embid, int(data['decisionWeiboID'][i]))
            if decision not in seen_count:
                seen_count[decision] = float(self.followee_count[user])
                retw_count[decision] = 1.0
            else:
                seen_count[decision] += self.followee_count[user]
                retw_count[decision] += 1

            label = data['label'][i]
            processed += [(user, seen, seen_users, decision, label)]

        self.retw_prob = {}
        for k, v in seen_count.items():
            self.retw_prob[k] = retw_count[k] / seen_count[k]

        return processed

    def get_allWeiboIDs(self, df):
        for seen in df['seenWeiboIDs']:
            if len(seen) > 0:
                self.allWeiboIDs.update(list(map(int, seen.split('_'))))


    def gold(self):
        """ Return gold labels as a list. """
        return self.labels

    def __len__(self):
        return self.num_examples

    def __getitem__(self, key):
        if not isinstance(key, int):
            raise TypeError
        if key < 0 or key >= self.num_examples:
            raise IndexError
        batch = self.data[key]
        batch_size = len(batch)
        batch = list(zip(*batch))
        assert len(batch) == 5

        lens = [len(x) for x in batch[1]]
        batch, orig_idx = sort_all(batch, lens)

        user = torch.LongTensor(batch[0])
        seen = get_long_tensor(batch[1], batch_size)
        seen_users = get_long_tensor(batch[2], batch_size)
        decision = torch.LongTensor(batch[3])
        label = torch.LongTensor(batch[4])

        return user, seen, seen_users, decision, orig_idx, label

    def __iter__(self):
        for i in range(self.__len__()):
            yield self.__getitem__(i)

def get_long_tensor(tokens_list, batch_size):
    token_len = max(len(x) for x in tokens_list)
    tokens = torch.LongTensor(batch_size, token_len).fill_(constant.PAD_ID)
    for i, s in enumerate(tokens_list):
        tokens[i, :len(s)] = torch.LongTensor(s)
    return tokens

def sort_all(batch, lens):
    """ Sort all fields by descending order of lens, and return the original indices. """
    unsorted_all = [lens] + [range(len(lens))] + list(batch)
    sorted_all = [list(t) for t in zip(*sorted(zip(*unsorted_all), reverse=True))]
    return sorted_all[2:], sorted_all[1]

def map_emb_index(original_string, index_map):
    intermediate = list(map(int, original_string.split('_')))
    result = [index_map[b] if b in index_map else constant.UNK_WEIBO_ID for b in intermediate]
    return result

def EmbLoader(dict, idmap, opt):
    emb_size = len(idmap) + 1
    emb_dim = opt['emb_dim']
    emb_matrix = np.zeros((emb_size, emb_dim))

    for k, v in idmap.items():
        if k in dict:
            emb_matrix[v] = dict[k]
        else:
            emb_matrix[v] = np.zeros(emb_dim)

    return emb_matrix

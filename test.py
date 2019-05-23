import os
import argparse
import torch
import numpy as np
import random
import pickle
import time
from datetime import datetime
from utils import constant
# from utils.metrics import metrics
from utils.metrics import metrics, tune_thres, get_preds, tune_thres_new
from loader import DataLoader, EmbLoader
from model import ModelWrapper
from shutil import copyfile
import pickle
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--cuda', type=bool, default=torch.cuda.is_available())
parser.add_argument('--model', type=str, default='InfoLSTM')
parser.add_argument('--data_dir', type=str, default='./data/final')
parser.add_argument('--emb_file', type=str, default='./data/content_dict.pkl')
parser.add_argument('--followee_count_file', type=str, default='./data/followee_count.pkl')
parser.add_argument('--model_save_dir', type=str, default='./data/saved_model')
parser.add_argument('--idx_dict', type=str, default='./data/final/idx_dict.pkl')
parser.add_argument('--save_epoch', type=int, default=5, help='Save model checkpoints every k epochs.')

parser.add_argument('--hidden_dim', type=int, default=200, help='RNN hidden state size.')
parser.add_argument('--num_layers', type=int, default=2, help='Num of RNN layers.')
parser.add_argument('--dropout', type=float, default=0.5, help='Input and RNN dropout rate.')
parser.add_argument('--num_epoch', type=int, default=30)
parser.add_argument('--log_step', type=int, default=20, help='Print log every k steps.')

parser.add_argument('--window_size', type=int, default=10)

parser.add_argument('--patience', type=int, default=3)
parser.add_argument('--lr_decay', type=float, default=0.5)

parser.add_argument('--lr', type=float, default=1.0, help='Applies to SGD')
parser.add_argument('--max_grad_norm', type=float, default=5.0, help='Gradient clipping.')

parser.add_argument('--emb_dim', type=int, default=768)
parser.add_argument('--batch_size', type=int, default=256)
parser.add_argument('--seed', type=int, default=99)
# parser.add_argument('--cuda', type=bool, default=torch.cuda.is_available())
args = parser.parse_args()

torch.manual_seed(args.seed)
np.random.seed(args.seed)
random.seed(args.seed)

opt = vars(args)
print(opt)

with open(opt['idx_dict'], 'rb') as fin:
    weibo2embid = pickle.load(fin)

train_batch = DataLoader(os.path.join(opt['data_dir'], 'train.csv'),
                   opt['batch_size'],
                   opt,
                   weibo2embid=weibo2embid,
                   evaluation=False)
dev_batch = DataLoader(os.path.join(opt['data_dir'], 'dev.csv'),
                   opt['batch_size'],
                   opt,
                   weibo2embid=weibo2embid,
                   evaluation=True)
test_batch = DataLoader(os.path.join(opt['data_dir'], 'test.csv'),
                   opt['batch_size'],
                   opt,
                   weibo2embid=weibo2embid,
                   evaluation=True)

weibo2embid = train_batch.weibo2embid
model = ModelWrapper(opt, weibo2embid, train_batch.retw_prob)
model.load(os.path.join(opt['model_save_dir'], 'best_model.pt'))

all_probs = []
for i, b in enumerate(dev_batch):
    _, probs, _ = model.predict(b, thres=0.002)
    all_probs += probs

_, _, _, _, best_thres = tune_thres_new(dev_batch.gold(), all_probs)
# print('Best thres (dev): %.6f' % best_thres)

all_probs = []
for i, b in enumerate(test_batch):
    _, probs, _ = model.predict(b, thres=0.002)
    all_probs += probs

preds = get_preds(all_probs, best_thres)
accuracy, precision, recall, f1 = metrics(test_batch.gold(), preds)
auc, _, _, _, _ = tune_thres_new(test_batch.gold(), all_probs)

print('Auc: %.4f, Accuracy: %.4f, Precision: %.4f, Recall: %.4f, F1: %.4f' % (auc, accuracy, precision, recall, f1))
with open('./log.txt', 'a+') as fout:
    fout.write('\n' + time.asctime(time.localtime(time.time())))
    fout.write(' '.join(sys.argv))
    fout.write('Auc: %.4f, Accuracy: %.4f, Precision: %.4f, Recall: %.4f, F1: %.4f' % (auc, accuracy, precision, recall, f1))

pickle.dump(all_probs, open('./test_probs.pkl', 'wb'))
pickle.dump(test_batch.gold(), open('./test_gold.pkl', 'wb'))

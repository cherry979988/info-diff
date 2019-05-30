import os
import argparse
import torch
import numpy as np
import random
import time
from utils.metrics import metrics, tune_thres, get_preds, tune_thres_new
from loader import DataLoader, EmbLoader
from model import ModelWrapper
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
parser.add_argument('--penalty_coeff', type=float, default=0.5, help='Coefficient of Penalty term used in Clash model')
parser.add_argument('--num_epoch', type=int, default=30)
parser.add_argument('--log_step', type=int, default=20, help='Print log every k steps.')

parser.add_argument('--window_size', type=int, default=10)
parser.add_argument('--no_extra_linear', dest='use_extra_linear', action='store_false')
parser.add_argument('--use_extra_linear', dest='use_extra_linear', action='store_true')
parser.set_defaults(use_extra_linear=True)

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

# train_batch = DataLoader(os.path.join(opt['data_dir'], 'train.csv'),
#                    opt['batch_size'],
#                    opt,
#                    weibo2embid=weibo2embid,
#                    evaluation=False)
dev_batch = DataLoader(os.path.join(opt['data_dir'], 'dev.csv'),
                   opt['batch_size'],
                   opt,
                   weibo2embid=weibo2embid,
                   evaluation=True)

model = ModelWrapper(opt, weibo2embid, eva=True)
model.load(os.path.join(opt['model_save_dir'], 'best_model.pt'))

all_probs = []
all_preds = []
for i, b in enumerate(dev_batch):
    preds, probs, _ = model.predict(b, thres=0.5)
    all_probs += probs
    all_preds += preds

acc, prec, rec, dev_f1 = metrics(dev_batch.gold(), all_preds)
print('acc: {}, prec: {}, rec: {}, f1: {}\n'.format(acc, prec, rec, dev_f1))

auc, prec, rec, f1, best_thres = tune_thres_new(dev_batch.gold(), all_probs)
print('auc: {}, prec: {}, rec: {}, f1: {}, best_thres: {}'.format(auc, prec, rec, f1, best_thres))

with open('./log.txt', 'a+') as fout:
    fout.write('\n' + time.asctime(time.localtime(time.time())))
    fout.write(' '.join(sys.argv))
    fout.write('\nauc: {}, prec: {}, rec: {}, f1: {}, best_thres: {}\n'.format(auc, prec, rec, f1, best_thres))
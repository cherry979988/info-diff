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
from utils.metrics import metrics, tune_thres, get_preds
from loader import DataLoader, EmbLoader
from model import ModelWrapper
from shutil import copyfile

parser = argparse.ArgumentParser()
parser.add_argument('--cuda', type=bool, default=torch.cuda.is_available())
parser.add_argument('--model', type=str, default='InfoLSTM')
parser.add_argument('--data_dir', type=str, default='./data/final')
parser.add_argument('--emb_file', type=str, default='./data/content_dict.pkl')
parser.add_argument('--followee_count_file', type=str, default='./data/followee_count.pkl')
parser.add_argument('--model_save_dir', type=str, default='./data/saved_model')
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
# if args.cpu:
#     args.cuda = False
# elif args.cuda:
#     torch.cuda.manual_seed(args.seed)

# make opt
opt = vars(args)
print(opt)

train_batch = DataLoader(os.path.join(opt['data_dir'], 'train.csv'),
                   opt['batch_size'],
                   opt,
                   evaluation=False)

with open('./data/analysis/train_retweet_prob.pkl', 'wb') as fout:
    pickle.dump(train_batch.retw_prob, fout)
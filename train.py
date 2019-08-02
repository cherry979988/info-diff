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

parser = argparse.ArgumentParser()
parser.add_argument('--cuda', type=bool, default=torch.cuda.is_available())
parser.add_argument('--model', type=str, default='InfoLSTM')
parser.add_argument('--data_dir', type=str, default='./data/final')
parser.add_argument('--emb_file', type=str, default='./data/content_dict.pkl')
parser.add_argument('--idx_dict', type=str, default='./data/final/idx_dict.pkl')
parser.add_argument('--followee_count_file', type=str, default='./data/followee_count.pkl')
parser.add_argument('--model_save_dir', type=str, default='./data/saved_model')
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

parser.add_argument('--train_emb', dest='fix_emb', action='store_false')
parser.add_argument('--fix_emb', dest='fix_emb', action='store_true')
parser.set_defaults(fix_emb=False)

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
# test_batch = DataLoader(os.path.join(opt['data_dir'], 'test.csv'),
#                    opt['batch_size'],
#                    opt,
#                    weibo2embid=weibo2embid,
#                    evaluation=True)

if not os.path.exists(opt['model_save_dir']):
    os.makedirs(opt['model_save_dir'])

weibo2embid = train_batch.weibo2embid

model = ModelWrapper(opt, weibo2embid, train_batch.retw_prob)

global_step = 0
# current_lr = opt['lr']
max_steps = len(train_batch) * opt['num_epoch']

global_start_time = time.time()
format_str = '{}: step {}/{} (epoch {}/{}), loss = {:.6f} ({:.3f} sec/batch), lr: {:.6f}'

dev_f1_history = []

for epoch in range(1, opt['num_epoch'] + 1):
    train_loss = 0
    current_lr = model.optimizer.param_groups[0]['lr']

    for i, batch in enumerate(train_batch):
        start_time = time.time()
        global_step += 1
        loss = model.update(batch)
        train_loss += loss
        if global_step % opt['log_step'] == 0:
            duration = time.time() - start_time
            print(format_str.format(datetime.now(), global_step, max_steps, epoch, \
                                    opt['num_epoch'], loss, duration, current_lr))

    print("Evaluating on dev set ...")
    predictions = []
    probabilities = []
    dev_loss = 0
    for i, batch in enumerate(dev_batch):
        preds, probs, loss = model.predict(batch, thres=0.01)
        predictions += preds
        probabilities += probs
        dev_loss += loss

    train_loss = train_loss / train_batch.num_examples * opt['batch_size']  # avg loss per batch
    dev_loss = dev_loss / dev_batch.num_examples * opt['batch_size']
    model.scheduler.step(dev_loss)

    # _, _, _, dev_f1 = metrics(dev_batch.gold(), predictions)
    _, _, _, dev_f1, _ = tune_thres_new(dev_batch.gold(), probabilities)
    print("epoch {}: train_loss = {:.6f}, dev_loss = {:.6f}, dev_f1 = {:.4f}".format(epoch,\
            train_loss, dev_loss, dev_f1))

    model_file = os.path.join(opt['model_save_dir'], 'checkpoint_epoch_{}.pt'.format(epoch))
    model.save(model_file, epoch)
    if epoch == 1 or dev_f1 > max(dev_f1_history):
        copyfile(model_file, os.path.join(opt['model_save_dir'], 'best_model.pt'))
        print('new best model saved.')
    if epoch % opt['save_epoch'] != 0:
        os.remove(model_file)

    dev_f1_history += [dev_f1]
    print("")

# test_batch = DataLoader(opt['data_dir'] + '/test.csv', opt['batch_size'], opt, True)

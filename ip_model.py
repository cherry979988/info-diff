import argparse
import torch
from loader import DataLoader
from model import IPModel
import os
import pickle
from utils.metrics import metrics, tune_thres, get_preds, tune_thres_new

parser = argparse.ArgumentParser()
parser.add_argument('--cuda', type=bool, default=torch.cuda.is_available())
parser.add_argument('--data_dir', type=str, default='./data/final')
parser.add_argument('--emb_file', type=str, default='./data/content_dict.pkl')
parser.add_argument('--idx_dict', type=str, default='./data/final/idx_dict.pkl')
parser.add_argument('--followee_count_file', type=str, default='./data/followee_count.pkl')
parser.add_argument('--window_size', type=int, default=10)

parser.add_argument('--batch_size', type=int, default=256)
parser.add_argument('--seed', type=int, default=99)

args = parser.parse_args()
opt = vars(args)

torch.manual_seed(args.seed)
# np.random.seed(args.seed)
# random.seed(args.seed)
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

model = IPModel(train_batch.retw_prob, opt)

all_probs = []
for i, b in enumerate(dev_batch):
    _, probs = model.predict(b, thres=0.0)
    all_probs += probs

print('max prob: ', max(all_probs))
_, _, _, _, best_thres = tune_thres_new(dev_batch.gold(), all_probs) # , start=0.0, end=0.002, fold=1001)
print('Best thres (dev): %.8f' % best_thres)

all_probs = []
for i, b in enumerate(test_batch):
    _, probs = model.predict(b, thres=0.0)
    all_probs += probs

preds = get_preds(all_probs, best_thres)
accuracy, precision, recall, f1 = metrics(test_batch.gold(), preds)
print('Accuracy: %.4f, Precision: %.4f, Recall: %.4f, F1: %.4f' % (accuracy, precision, recall, f1))

# thres_to_test = [0.0, 0.00001, 0.0005, 0.001]
# for thres in thres_to_test:
#     preds = get_preds(all_probs, thres)
#     accuracy, precision, recall, f1 = metrics(test_batch.gold(), preds)
#
#     print('Accuracy: %.4f, Precision: %.4f, Recall: %.4f, F1: %.4f' % (accuracy, precision, recall, f1))
# print('Tunning on test...')
# print('max prob: ', max(all_probs))
# _, _, _, _, best_thres = tune_thres(test_batch.gold(), all_probs, start=0.0, end=0.002, fold=1001)
# print('Best thres (dev): %.8f' % best_thres)
#
# preds = get_preds(all_probs, best_thres)
# accuracy, precision, recall, f1 = metrics(test_batch.gold(), preds)
# print('Accuracy: %.4f, Precision: %.4f, Recall: %.4f, F1: %.4f' % (accuracy, precision, recall, f1))
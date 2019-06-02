import argparse
from sklearn.manifold import TSNE
import pickle
import numpy as np
import torch
import os
from loader import EmbLoader
from model import ModelWrapper
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn')


parser = argparse.ArgumentParser()
parser.add_argument('--emb_file', type=str, default='./data/content_dict.pkl')
parser.add_argument('--model', type=str, default='Clash')
parser.add_argument('--idx_dict', type=str, default='./data/final/idx_dict.pkl')
parser.add_argument('--tsne_dump', type=str, default='./data/final/tsne_dump.pkl')
parser.add_argument('--key_id', type=int, default=113)

parser.add_argument('--cuda', type=bool, default=torch.cuda.is_available())
parser.add_argument('--data_dir', type=str, default='./data/final')
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

parser.add_argument('--run_tsne', dest='tsne', action='store_true')
parser.set_defaults(tsne=False)
args = parser.parse_args()

opt = vars(args)

def cos_sim(a,b):
    num = np.sum(np.multiply(a, b))
    denom = np.linalg.norm(a) * np.linalg.norm(b) + 1e-10
    cos = num / denom
    return cos

with open(opt['emb_file'], 'rb') as fin:
    emb = pickle.load(fin)

with open(opt['idx_dict'], 'rb') as fin:
    weibo2embid = pickle.load(fin)

emb_matrix = EmbLoader(emb, weibo2embid, opt)

if opt['tsne']:
    print('Original shape: ', np.shape(emb_matrix))

    tsne = TSNE(n_components=2, random_state=0)
    np.set_printoptions(suppress=True)
    output = tsne.fit_transform(emb_matrix)

    print('Current shape: ', np.shape(output))

    with open(opt['tsne_dump'], 'wb') as fout:
        pickle.dump(output, fout)

else:
    with open(opt['tsne_dump'], 'rb') as fin:
        output = pickle.load(fin)

key_emb = emb_matrix[opt['key_id'], :]

bert_sim = []
for i in range(len(emb_matrix)):
    bert_sim.append(cos_sim(key_emb, emb_matrix[i, :]))

if not os.path.exists(os.path.join(opt['model_save_dir'], 'plot')):
    os.mkdir(os.path.join(opt['model_save_dir'], 'plot'))

fig = plt.figure()
cset = plt.scatter(output[:, 0], output[:, 1], s=8, c=bert_sim, cmap='PuBu')
plt.plot(output[opt['key_id'], 0], output[opt['key_id'], 1], 'r.')
plt.colorbar(cset)
plt.savefig(os.path.join(opt['model_save_dir'], 'plot', '%d_bert_sim' % opt['key_id']))

fig = plt.figure()
plt.hist(bert_sim, bins=100)
plt.savefig(os.path.join(opt['model_save_dir'], 'plot', '%d_bert_hist' % opt['key_id']))


model = ModelWrapper(opt, weibo2embid, eva=True)
model.load(os.path.join(opt['model_save_dir'], 'best_model.pt'))

clash_delta = []
for i in range(len(emb_matrix)):
    emb1 = torch.tensor([i]).cuda()
    emb2 = torch.tensor([opt['key_id']]).cuda()
    clash_delta.append(model.model.get_delta(emb1, emb2).item())

ceil = max(max(clash_delta), min(clash_delta) * (-1)) * 1.05
print(max(clash_delta), min(clash_delta))
fig = plt.figure()
cset = plt.scatter(output[:, 0], output[:, 1], s=8, c=clash_delta, cmap='PuBu', vmin=-ceil, vmax=ceil)
plt.plot(output[opt['key_id'], 0], output[opt['key_id'], 1], 'r.')
plt.colorbar(cset)
plt.savefig(os.path.join(opt['model_save_dir'], 'plot', '%d_clash_delta' % opt['key_id']))

fig = plt.figure()
plt.hist(clash_delta, bins=100)
plt.savefig(os.path.join(opt['model_save_dir'], 'plot', '%d_clash_hist' % opt['key_id']))

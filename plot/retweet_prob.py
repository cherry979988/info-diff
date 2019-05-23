import matplotlib
from matplotlib.font_manager import *
import matplotlib.pyplot as plt
plt.style.use('seaborn')
import pickle
import numpy as np

with open('./data/analysis/train_retweet_prob.pkl', 'rb') as fin:
    tweet_prob = pickle.load(fin)

all_probs = list(tweet_prob.values())
print(np.percentile(all_probs, 10), np.percentile(all_probs, 90))
bin = [i * 0.0005 for i in range(40)]

myfont = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', size=14)

fig = plt.figure(figsize=(7,4))
plt.hist(all_probs, bins=bin)
# plt.title(u'训练集中微博转发概率直方图', fontproperties=myfont)
# plt.show()

plt.savefig('./data/analysis/retweet_prob', dpi=400)
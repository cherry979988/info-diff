import matplotlib
# Use 'Agg' so this program could run on a remote server
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn')
import numpy as np

weibo = [176, 236, 313, 392, 411]
twitter = [288, 305, 318, 330, 336]

x=np.arange(5)
fig = plt.figure(figsize=(8,4))
plt.bar(x, weibo, width=0.3, label='Weibo')
for i, v in enumerate(weibo):
    plt.text(x[i], v + 10, str(v), size=12, ha='center')
plt.bar(x + 0.4, twitter, width=0.3, label='Twitter')
for i, v in enumerate(twitter):
    plt.text(x[i] + 0.4, v + 10, str(v), size=12, ha='center')

plt.ylim(100, 500)

plt.legend(loc='upper left')
plt.xticks(x + 0.2, ['2014', '2015', '2016', '2017', '2018 Q1'])
plt.show()
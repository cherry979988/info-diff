import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn')
import numpy as np

f1 = [28.94, 32.28, 55.81, 56.17, 64.84, 64.84]
err = [0.00, 1.86, 7.61, 4.86, 0.09, 0.09]

auc = [15.80, 26.86, 52.24, 50.30, 68.77, 68.77]
erra = [0.00, 1.00, 10.40, 9.23, 0.07, 0.07]

xlabel = ['IP', 'IMM', 'IMM Enhanced', 'IMM Enhanced (fix)', 'InfoLSTM', 'InfoLSTM (fix)']

fig = plt.figure(figsize=(6, 4))

x = np.arange(len(f1))

plt.bar(x, auc, yerr=erra, width=0.2)
plt.bar(x + 0.3, f1, yerr=err, width=0.2)
plt.ylabel('Score (%)')
plt.xticks(x + 0.15, xlabel, rotation=25, ha='right')

plt.legend(['AUC', 'F1'], loc='upper left')
plt.show()
#plt.savefig('./data/saved_model/overall_score_compare')

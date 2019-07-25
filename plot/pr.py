import sklearn.metrics
import matplotlib

# Use 'Agg' so this program could run on a remote server
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn')
import numpy as np
import sys
import os

result_dir = './data/saved_model'

model_name = 'InfoLSTM'
prefix = 'infolstm-final'

# parDir = ['ip','Clash-final-lr1-2', 'Clash_Enhanced-final-3', 'infolstm-final-2']
# labels = ['IP', 'Clash', 'Clash_Enhanced', 'InfoLSTM']
# num = [1, 5, 5, 5]

def main():
    fig = plt.figure(figsize=(6, 5))

    for j in range(1, 6):
        dir = prefix + '-' + str(j)
        x = np.load(os.path.join(result_dir, dir, model_name + '_x' + '.npy'))
        y = np.load(os.path.join(result_dir, dir, model_name + '_y' + '.npy'))
        f1 = (2 * x * y / (x + y + 1e-20)).max()
        auc = sklearn.metrics.auc(x=x, y=y)
        # plt.plot(x, y, lw=2, label=model + '-auc='+str(auc))
        plt.plot(x, y, lw=2, label="{} Run {}".format(model_name, j))
        print(model_name + ' : ' + 'auc = ' + str(auc) + ' | ' + 'max F1 = ' + str(f1))
        print('    P@100: {} | P@200: {} | P@300: {} | Mean: {}'.format(y[100], y[200], y[300],
                                                                        (y[100] + y[200] + y[300]) / 3))

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.0])
    plt.xlim([0.0, 1.0])
    plt.title('Precision-Recall')
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.savefig(os.path.join(result_dir, model_name + '_pr_curve'))


if __name__ == "__main__":
    main()

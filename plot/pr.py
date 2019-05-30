import sklearn.metrics
import matplotlib

# Use 'Agg' so this program could run on a remote server
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn')
import numpy as np
import sys
import os

result_dir = './data/for-plot'

# parDir = ['ip','Clash-final-lr1-2', 'Clash_Enhanced-final-3', 'infolstm-final-2']
models = ['IP', 'Clash', 'Clash_Enhanced', 'InfoLSTM']
num = [1, 5, 5, 5]

def main():
    for i, model in enumerate(models):
        for j in range(1, num[i] + 1):
            x = np.load(os.path.join(result_dir, model, str(j), model + '_x' + '.npy'))
            y = np.load(os.path.join(result_dir, model, str(j), model + '_y' + '.npy'))
            f1 = (2 * x * y / (x + y + 1e-20)).max()
            auc = sklearn.metrics.auc(x=x, y=y)
            # plt.plot(x, y, lw=2, label=model + '-auc='+str(auc))
            plt.plot(x, y, lw=2, label=model)
            print(model + ' : ' + 'auc = ' + str(auc) + ' | ' + 'max F1 = ' + str(f1))
            print('    P@100: {} | P@200: {} | P@300: {} | Mean: {}'.format(y[100], y[200], y[300],
                                                                            (y[100] + y[200] + y[300]) / 3))

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.0])
    plt.xlim([0.0, 1.0])
    plt.title('Precision-Recall')
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.savefig(os.path.join(result_dir, 'pr_curve'))


if __name__ == "__main__":
    main()

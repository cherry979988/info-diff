import numpy as np
import os
import time
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.svm import LinearSVC
import sys
import random

#os.chdir('D:\\Users\\tc\\retweet\\baseline\\final')

if len(sys.argv) < 3:
        print('please select w and feature');
        exit(0);

selected = [1];

for i in range(22):
        selected.append(0);

print('the features you selected are:');

w = float(sys.argv[1]);
print('w = ' + str(w));

for i in range(2, len(sys.argv)):
        idx = int(sys.argv[i]);
        selected[idx + 1] = 1;
        print(str(idx) + ' ');

log = open('log.txt', 'w')
ins = open('ins.txt', 'r')
res = open('res.txt', 'w');

x0 = [[], [], [], [], []];
y0 = [[], [], [], [], []];

n = 0;

while 1:
        n = n + 1;
        if n % 1000 == 0:
                print n;
        line = ins.readline();
        if not line:
                break;
        tmpstr = line.split(' ');
        tmp0 = [];
        for i in range(len(tmpstr) - 1):
                tmp0.append(float(tmpstr[i]))
        tmp0.append(w * (tmp0[9] + tmp0[11]) + (1 - w) * tmp0[19]);
        tmp = [];
        for i in range(len(tmp0)):
                if selected[i]:
                        tmp.append(tmp0[i]);
        idx = int(random.random() / 0.2);
#        print('idx = ' + str(idx));
#        print('sz = ' + str(len(tmp)));
        x0[idx].append(tmp[1:]);
        y0[idx].append(tmp[0]);

print('Let\'s Go!')

dim = len(x0[0][0]);
coe = [];
for i in range(dim):
        coe.append(0);
        
tpt = 0; tnt = 0; fpt = 0; fnt = 0; hitt = 0; misst = 0;

last = time.clock()
for cnt in range(5):
        x = []; y = [];
        x_test = []; y_test = [];
        for i in range(5):
                for j in range(len(y0[i])):
                        if i == cnt:
                                x_test.append(x0[i][j]);
                                y_test.append(y0[i][j]);
                        else:
                                x.append(x0[i][j]);
                                y.append(y0[i][j]);
        
        clf = LogisticRegression().fit(x, y)
        pred = clf.predict_proba(x_test)
        hit = 0
        miss = 0
        tp = 0
        tn = 0
        fp = 0
        fn = 0
        for i in xrange(len(pred)):
                res.write(str(int(y_test[i])) + ' ' + str(pred[i][1]) + '\n');
                if (pred[i][0] > pred[i][1]):
                        if (y_test[i] == 0):
                                hit += 1
                                tn += 1
                        else:
                                miss += 1
                                fn += 1
                else:
                        if (y_test[i] == 1.0):
                                hit += 1
                                tp += 1
                        else:
                                miss += 1
                                fp += 1
        print('tp = ' + str(tp));
        print('fp = ' + str(fp));
        print('tn = ' + str(tn));
        print('fn = ' + str(fn));

        tpt = tpt + tp;
        fpt = fpt + fp;
        tnt = tnt + tn;
        fnt = fnt + fn;
        hitt = hitt + hit;
        misst = misst + miss;
        precision = tp/float(tp+fp)
        recall = tp/float(tp+fn)
        f1 = 2*precision*recall/(precision+recall)
        print('LR: '+str(hit/float(hit+miss))+'\nprecision:'+str(precision)+':\nrecall:'+str(recall)+'\nf1:'+str(f1)+'\nmodel'+str(clf.coef_))
        log.write('LR: '+str(hit/float(hit+miss))+'\nprecision:'+str(precision)+':\nrecall:'+str(recall)+'\nf1:'+str(f1)+'\nmodel'+str(clf.coef_)+'\n')
        log.write('\n\n');
        for j in range(dim):
                coe[j] = coe[j] + clf.coef_[0][j] / 5.0;
                
precision = tpt/float(tpt+fpt)
recall = tpt/float(tpt+fnt)
f1 = 2*precision*recall/(precision+recall)
log.write('\nLR: '+str(hitt/float(hitt+misst))+'\nprecision:'+str(precision)+'\nrecall:'+str(recall)+'\nf1:'+str(f1) + '\n')
log.write('coe:' +str(coe) + '\n');

current = time.clock()
log.close();
res.close();
ins.close();

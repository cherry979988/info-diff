import sklearn.metrics
import numpy as np

def metrics(gold, pred):
    assert len(gold) == len(pred)
    tp, tn, fp, fn = 0.0, 0.0, 0.0, 0.0
    eps = 1e-6
    for i, item in enumerate(zip(gold, pred)):
        g, p = item
        if g == 1 and p == 1:
            tp += 1
        elif g == 1 and p == 0:
            fn += 1
        elif g == 0 and p == 0:
            tn += 1
        elif g == 0 and p == 1:
            fp += 1
    accuracy = (tp + tn) / (tp + tn + fn + fp + eps)
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)
    if tp == 0:
        f1 = 0.0
    else:
        f1 = (2 * precision * recall) / (precision + recall)
    return accuracy, precision, recall, f1

def tune_thres(label, probs, start=0.0, end=1.0, fold=101):
    print('start tuning:')
    delta = (end - start) / (fold - 1)
    thres_list = [start + delta * i for i in range(fold)]
    # print(thres_list)

    best_thres = 0.0
    best_acc, best_prec, best_rec, best_f1 = 0.0, 0.0, 0.0, 0.0

    for thres in thres_list:
        preds = get_preds(probs, thres)
        acc, prec, rec, f1 = metrics(label, preds)
        # print(thres, acc, prec, rec, f1)
        if f1 > best_f1:
            best_acc, best_prec, best_rec, best_f1 = acc, prec, rec, f1
            best_thres = thres

    return best_acc, best_prec, best_rec, best_f1, best_thres

def get_preds(probs, thres):
    return list(map(lambda x: int(x > thres), probs))

def tune_thres_new(label, probs):
    assert len(label) == len(probs)
    all_retweet = sum(label)
    result = [(lab, prob) for lab, prob in zip(label, probs)]
    sorted_result = sorted(result, key=lambda x: x[1], reverse=True)
    prec = []
    recall = []
    correct = 0
    # print(sorted_result[:20])
    for i, item in enumerate(sorted_result):
        correct += item[0]
        prec.append(float(correct) / (i+1))
        recall.append(float(correct) / all_retweet)
    auc = sklearn.metrics.auc(x=recall, y=prec)
    print('\n[TUNE] auc: {}'.format(auc))

    prec = np.array(prec)
    recall = np.array(recall)
    f1 = 2 * prec * recall / (prec + recall + 1e-10)

    idx = np.argmax(f1)
    print('\n[TUNE] best thres: {}, prec: {}, recall: {}, f1: {}'.format(sorted_result[idx][1], prec[idx], recall[idx], f1[idx]))

    return auc, prec[idx], recall[idx], f1[idx], sorted_result[idx][1]
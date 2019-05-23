import torch
import argparse
import pickle
import os
import sys
import time
from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForMaskedLM
from multiprocessing import Process

parser = argparse.ArgumentParser()
parser.add_argument('--bert_dir', type=str, default='./data/pretrained_model/bert-base-chinese')
parser.add_argument('--n_process', type=int, default=4)
parser.add_argument('--input', type=str, default='./data/root_content.txt')
parser.add_argument('--output_dir', type=str, default='./data/embedding')

args = parser.parse_args()
opt = vars(args)


def worker(id, parse_list):

    tokenizer = BertTokenizer.from_pretrained(opt['bert_dir'])
    model = BertModel.from_pretrained(opt['bert_dir'])
    model.eval()

    def get_emb(sentence):
        tokenized = tokenizer.tokenize(sentence)

        indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized)
        segments_ids = [0] * len(tokenized)

        tokens_tensor = torch.tensor([indexed_tokens])
        segments_tensors = torch.tensor([segments_ids])

        with torch.no_grad():
            encoded_layers, _ = model(tokens_tensor, segments_tensors)

        return encoded_layers[-1][0][0].numpy()

    print('Thread %d, Starting... ' % id)
    start_time = time.time()

    vec_dict = {}
    for i, (k, v) in enumerate(parse_list):
        vec_dict[k] = get_emb(v)
        if i % 10 == 0:
            sys.stdout.write("Process %d, parsed %d users, Time: %d sec\r" % (id, i, time.time() - start_time))
            sys.stdout.flush()
    with open(os.path.join(opt['output_dir'], 'tmp%d.pkl' % id), 'rb') as output:
        pickle.dump(vec_dict, output)


def main(opt):
    if not os.path.exists(opt['output_dir']):
        os.mkdir(opt['output_dir'])

    with open(opt['input'], 'r', encoding='gb18030') as fin:
        lines = fin.readlines()

    parse_list = []

    for i in range(0, len(lines), 2):
        weiboID = lines[i].strip()
        content = lines[i+1].strip()
        parse_list.append((weiboID, content))

    n = len(parse_list)
    each_proc = int(n / opt['n_process'])
    print('%d weibos in total, %s weibos in each thread.' % (n, each_proc))

    # vec_dict = {}
    # for i, (k, v) in enumerate(parse_list):
    #     vec_dict[k] = get_emb(v)
    #     if i % 50 == 0:
    #         sys.stdout.write("parsed %d users\r" % i)
    #         sys.stdout.flush()
    #
    # with open(os.path.join(opt['output_dir'], 'vec_dict.pkl' % id), 'rb') as fout:
    #     pickle.dump(vec_dict, fout)

    procs = []
    for i in range(opt['n_process'] - 1):
        p = Process(target=worker, args=(i + 1, parse_list[i * each_proc:(i + 1) * each_proc]))
        p.start()
        procs.append(p)

    p = Process(target=worker, args=(opt['n_process'], parse_list[(opt['n_process'] - 1) * each_proc:]))
    p.start()
    procs.append(p)

    for proc in procs:
        proc.join()

if __name__ == '__main__':
    main(opt)
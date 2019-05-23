import argparse
import pickle
import pandas as pd
import numpy as np
import os


parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, default='./data/final')
parser.add_argument('--input_file', type=str, default='all.csv')
parser.add_argument('--train_ratio', type=float, default=0.8)
parser.add_argument('--dev_ratio', type=float, default=0.1)
parser.add_argument('--output_dir', type=str, default='./data/final-small-scale')
parser.add_argument('--random_seed', type=int, default=99)

args = parser.parse_args()

opt = vars(args)

def main(opt):
    assert opt['train_ratio'] + opt['dev_ratio'] < 1

    if not os.path.exists(opt['output_dir']):
        os.mkdir(opt['output_dir'])

    df = pd.read_csv(os.path.join(opt['input_dir'], opt['input_file']))
    df = df.sample(frac=0.01, random_state=opt['random_seed'])

    n = len(df)
    n_train = int(n * opt['train_ratio'])
    n_dev = int(n * opt['dev_ratio'])
    n_test = n - n_train - n_dev

    df_train = df[:n_train]
    df_dev = df[n_train: n_train + n_dev]
    df_test = df[n_train + n_dev:]

    df_train.to_csv(os.path.join(opt['output_dir'], 'train.csv'))
    df_dev.to_csv(os.path.join(opt['output_dir'], 'dev.csv'))
    df_test.to_csv(os.path.join(opt['output_dir'], 'test.csv'))

    print('Splitting done..\n\n%d train instances\n%d dev instances\n%d test instances' % (n_train, n_dev, n_test))
    print('File saved to %s' % opt['output_dir'])

if __name__ == '__main__':
    main(opt)
import pandas as pd
import os
import sys
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, default='./data/instances')
parser.add_argument('--output_file', type=str, default='./data/merged_instances.csv')

args = parser.parse_args()
opt = vars(args)

columns = ['username', 'seenWeiboIDs', 'seenWeiboUsers', 'decisionWeiboID', 'label']

def main(opt):
    df = pd.DataFrame(columns=columns)
    file_list = os.listdir(opt['input_dir'])

    print('%d files in total ... ' % len(file_list))
    start_time = time.time()

    for i, file in enumerate(file_list):
        df0 = pd.read_csv(os.path.join(opt['input_dir'], file))
        df = df.append(df0, ignore_index=True)

        if i % 50 == 0:
            sys.stdout.write("Parsed %d users, Time: %d sec\r" % (i, time.time() - start_time))
            sys.stdout.flush()

        if i == 50:
            break

    df.to_csv(opt['output_file'])


if __name__ == '__main__':
    main(opt)
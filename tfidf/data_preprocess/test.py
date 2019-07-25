import os
import pandas as pd
import argparse

'''transfer user_profile*.txt to a csv file'''
parser = argparse.ArgumentParser()
parser.add_argument('--input_file', type=str, default='./data/weibo_dataset/userProfile/user_profile1.txt')
args = parser.parse_args()
opt = vars(args)

def main(opt):
    headers = ['id', 'bi_followers_count', 'city',
               'verified', 'followers_count', 'location',
               'province', 'friends_count', 'name',
               'gender', 'created_at', 'verified_type',
               'statuses_count', 'description']
    df = pd.DataFrame(columns=headers)

    with open(opt['input_file'], 'r', encoding='gb18030') as f:

        # pass the headers
        for i in range(15):
            line = f.readline()

        idx = 0
        while True:
            try:
                _raw = [f.readline() for i in range(15)]
                # _parsed = [_raw[i] for i in range(0, 25, 2)]
                df.loc[idx] = _raw[:-1]
                idx += 1
                if idx % 100 == 0:
                    df.to_csv('./userProfile.csv', index=False)
            except:
                print('End of File')
                break

        print(df.head())

    df.to_csv('./userProfile.csv', index=False)

if __name__ == '__main__':
    main(opt)



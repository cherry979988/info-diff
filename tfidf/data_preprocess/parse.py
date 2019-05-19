import pandas as pd
import argparse
import re

'''transfer Root_Content.txt to a csv file'''
parser = argparse.ArgumentParser()
parser.add_argument('--input_file', type=str, default='./data/weibo_dataset/weibocontents/Root_Content.txt')
args = parser.parse_args()
opt = vars(args)

FIRST_LINE_PATTERN = '^[0-9]{10,20}$'
FIRST_LINE_REGEX = re.compile(FIRST_LINE_PATTERN)

def isFirstLine(line):
    if FIRST_LINE_REGEX.findall(line):
        return True
    else:
        return False

def main(opt):
    headers = ['weiboID', 'content', 'at', 'link']
    df = pd.DataFrame(columns=headers)

    with open(opt['input_file'], 'r', encoding='gb18030') as f:
        buff = []
        idx = 0
        while True:
            try:
                line = f.readline().strip()
                if isFirstLine(line) and len(buff) > 0:
                    if len(buff) == 2:
                        buff = buff + ['', '']
                    elif len(buff) == 3:
                        if not buff[2].startswith('@'):
                            buff = [buff[0], buff[1], '', buff[2]]
                        else:
                            buff = buff + ['']
                    df.loc[idx] = buff
                    del buff
                    buff = [line]
                    idx += 1
                    if idx % 100 == 0:
                        df.to_csv('./Root_Content.csv', index=False)
                else:
                    buff.append(line)
            except:
                print('End of File')
                break

        print(df.head())
    df.to_csv('./userProfile.csv', index=False)

if __name__ == '__main__':
    main(opt)
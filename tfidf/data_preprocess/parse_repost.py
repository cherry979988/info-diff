import pandas as pd
import argparse
import re

'''transfer Root_Content.txt to a csv file'''
parser = argparse.ArgumentParser()
parser.add_argument('--input_file', type=str, default='./data/weibo_dataset/weibocontents/Retweet_Content.txt')
args = parser.parse_args()
opt = vars(args)

MID_PATTERN = '^[0-9]{14,20}\ '
MID_REGEX = re.compile(MID_PATTERN)

UID_PATTERN = '^[0-9]{6,12}$'
UID_REGEX = re.compile(UID_PATTERN)

def isOrigStartLine(line):
    return len(MID_REGEX.findall(line)) > 0

def isRepostStartLine(line):
    return len(UID_REGEX.findall(line)) > 0

def main(opt):
    headers = ['weiboID', 'content', 'at', 'link']
    df = pd.DataFrame(columns=headers)

    with open(opt['input_file'], 'r', encoding='gb18030') as f:
        buff = []
        idx = 0
        currentLine = None
        while True:
            try:
                lastLine = currentLine
                currentLine = f.readline().strip()
                if isOrigStartLine(currentLine) and lastLine:
                    next_first_line = getRepost(df, f)
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
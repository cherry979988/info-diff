import argparse
from Keyword import *

parser = argparse.ArgumentParser()
parser.add_argument('--dir', type=str, default='./data')
parser.add_argument('--keyword1', type=str, default='重庆公交车')
parser.add_argument('--keyword2', type=str, default='疫苗事件')

args = parser.parse_args()
opt = vars(args)

keyword1 = Keyword(opt['keyword1'], opt['dir'])
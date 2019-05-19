import argparse
import pandas as pd
import os
import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn')
from matplotlib.font_manager import *
myfont = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
import numpy as np

parser = argparse.ArgumentParser()
# parser.add_argument('--data_dir', type=str, default='../data/')
parser.add_argument('--summary_dir', type=str, default='../data/summary/')
parser.add_argument('--keyword1', type=str, default='孟晚舟')
parser.add_argument('--keyword2', type=str, default='加拿大前外交官')
parser.add_argument('--startdate', type=str, default='2018-12-11')
parser.add_argument('--enddate', type=str, default='2018-12-15')
parser.add_argument('--freq', type=str, default='1H')
args = parser.parse_args()
opt = vars(args)

def main(opt):
	filename1 = os.path.join(opt['summary_dir'], '%s_timestamp.csv' % opt['keyword1'])
	df1 = pd.read_csv(filename1)
	filename2 = os.path.join(opt['summary_dir'], '%s_timestamp.csv' % opt['keyword2'])
	df2 = pd.read_csv(filename2)

	split_list = pd.date_range(opt['startdate'], opt['enddate'], freq=opt['freq'])

	cumsum = map(lambda x: len(df1[df1['timestamp'] < str(x)]), split_list)
	result1 = list(cumsum)

	cumsum = map(lambda x: len(df2[df2['timestamp'] < str(x)]), split_list)
	result2 = list(cumsum)

	result3 = []
	result4 = []
	result5 = []

	for item in split_list:
		k1userlst = set(df1[df1['timestamp'] < str(item)]['userID'].tolist())
		k2userlst = set(df2[df2['timestamp'] < str(item)]['userID'].tolist())

		result3.append(len(k1userlst - k2userlst))
		result4.append(len(k2userlst - k1userlst))
		result5.append(len(k1userlst & k2userlst))

	fig = plt.figure(figsize=(8, 4))
	plt.rcParams['figure.dpi'] = 400
	plt.plot(result1)
	plt.plot(result2)
	plt.plot(result3)
	plt.plot(result4)
	plt.plot(result5)
	plt.legend(['只转发A消息',
				'只转发B消息',
				'转发A消息但不转发B消息',
				'转发B消息但不转发A消息',
				'A、B消息均转发'], prop=myfont)
	plt.title('“' + opt['keyword1'] + '事件”(A)与“' + opt['keyword2']+'事件”(B)消息转发情况', fontproperties=myfont)
	text = list(map(str, split_list[::12]))
	for i in range(1, len(text), 2):
		tmp = str(text[i]).split(' ')
		text[i] = text[i][-8:]
	plt.xticks(np.arange(0, len(split_list), 12), text, rotation=45, ha='right')
	fig_name = '_'.join([
		opt['keyword1'], opt['keyword2'],
		opt['startdate'], opt['enddate'],
		opt['freq']
	])
	plt.subplots_adjust(bottom=0.3)
	plt.savefig(os.path.join(opt['summary_dir'], fig_name), dpi=600)

	dfe = pd.DataFrame(columns=['time', 'FA', 'FB', 'FANB', 'FBNA', 'FAFB'])
	dfe['time'] = split_list
	dfe['FA'] = result1
	dfe['FB'] = result2
	dfe['FANB'] = result3
	dfe['FBNA'] = result4
	dfe['FAFB'] = result5
	dfe.to_csv(os.path.join(opt['summary_dir'], fig_name + '.csv'))

if __name__ == "__main__":
	main(opt)
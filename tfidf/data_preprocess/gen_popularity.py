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
parser.add_argument('--data_dir', type=str, default='../data/')
parser.add_argument('--summary_dir', type=str, default='../data/summary/')
parser.add_argument('--keyword', type=str, default='孟晚舟')
parser.add_argument('--startdate', type=str, default='2018-12-11')
parser.add_argument('--enddate', type=str, default='2018-12-15')
parser.add_argument('--freq', type=str, default='1H')
args = parser.parse_args()
opt = vars(args)

def gen_list(startdate, enddate):
	ret = []
	current_time = datetime.strptime(startdate, "%Y-%m-%d")
	end_time = datetime.strptime(enddate, "%Y-%m-%d") + datetime.timedelta(day=1)

	while current_time < end_time:
		ret.append(current_time.strftime("%Y-%m-%d %H:%M:%S"))
		current_time += datetime.timedelta(hours=2)

	return ret

def main(opt):
	## 先把原文和转发都读进来，只保留用户名和时间
	filename = os.path.join(opt['data_dir'], opt['keyword'], 'content.csv')

	df = pd.read_csv(filename)

	weiboIDs = df['weiboID']

	userIDs = df['userID']
	timestamps = df['timestamp']

	for weiboID in weiboIDs:
		filename_repost = os.path.join(opt['data_dir'], opt['keyword'], 'repost', weiboID + '.csv')
		try:
			df2 = pd.read_csv(filename_repost)
			userIDs = userIDs.append(df2['userID'])
			timestamps = timestamps.append(df2['time'])
		except:
			pass
		# 	print('file %s not found' % (weiboID + '.csv'))

	df3 = pd.DataFrame(columns=['userID', 'timestamp'])
	df3['userID'] = userIDs
	df3['timestamp'] = timestamps

	## 按照用户名为第一关键词，时间为第二关键词，排序
	df3.sort_values(by=['userID', 'timestamp'], inplace=True)
	# print(df3.head(100))
	print(len(df3))

	## 筛选出每个用户第一次转发的时间
	df3.drop_duplicates(subset=['userID'], keep='first', inplace=True)
	print(len(df3))

	## 按照时间排序
	df3.sort_values(by=['timestamp'], inplace=True)
	df3.to_csv(os.path.join(opt['summary_dir'], '%s_timestamp.csv' % opt['keyword']))

	## 画图
	time_series = df3['timestamp'].reset_index(drop=True)
	# print(time_series.head(20))
	# opt['startdate'] = time_series[0][:10]
	# opt['enddate'] = time_series[len(df3)-1][:10]
	# print(opt['startdate'], opt['enddate'])

	split_list = pd.date_range(opt['startdate'], opt['enddate'], freq=opt['freq'])

	cumsum = map(lambda x: len(df3[df3['timestamp']<str(x)]), split_list)
	result = list(cumsum)
	# print(result)


	plt.plot(result)
	plt.title(opt['keyword'], fontproperties=myfont)
	# n = len(time_series)
	plt.xticks(np.arange(0, len(split_list), 12), split_list[::12], rotation=45, ha='right')
	fig_name = '_'.join([
		opt['keyword'],
		opt['startdate'],
		opt['enddate'],
		opt['freq']
	])
	plt.subplots_adjust(left=0.2, bottom=0.3)
	plt.savefig(os.path.join(opt['summary_dir'], fig_name))

	df4 = pd.DataFrame()
	df4['time'] = split_list
	df4['n_repost'] = result
	df4.to_csv(os.path.join(opt['summary_dir'], fig_name + '.csv'))

if __name__ == "__main__":
	main(opt)
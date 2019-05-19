import os
import numpy as np

num_topics = 100
#num_topics = 500

os.chdir('f:')

print('loading retweeet_root.txt...')
file = open('retweeter_root.txt')
data = file.read().split('\n')[:-1]
author = []
for each in data:
	temp =  each.split('\t')
	length = len(temp) - 1
	author_temp = [length]
	for each2 in temp:
		author_temp.append(int(each2))
	author.append(author_temp[:])
	
#data = np.loadtxt('doc')
#doc_topics = dict()
#for each in data:
#	doc_topics[int(each[1])] = each[2:]
	
print('loading retweeet_root.txt...')
file = open('doc')
data = file.read().split('\n')[1:-1]
doc_topics = dict()
for tweet in data:
	meta = tweet.split('\t')
	temp = np.zeros(num_topics)
	for i in range(1, (len(meta)-2)/2):
		temp[int(meta[i*2])] = float(meta[i*2+1])
	doc_topics[int(meta[1])] = temp

def calculate_l1(tweets):
	global doc_topics
	distribution = np.zeros(num_topics)
	for index in tweets:
		distribution += doc_topics[index]
	sum = distribution.sum()
	for i in xrange(num_topics):
		distribution[i] /= sum
	return distribution

def calculate_l2(tweets):
	# bug: not sum up to one..
	global doc_topics
	distribution = np.zeros(num_topics)
	for index in tweets:
		distribution += doc_topics[index]
	sum = 0
	for each in distribution:
		sum += each * each
	sum = np.sqrt(sum)
	for i in xrange(num_topics):
		distribution[i] /= sum
	return distribution
		
		
print('start computing..')
file1 = open('author-topic-l1.txt', 'w')
file2 = open('author-topic-l2.txt', 'w')
file1.write('#author_id\tnum_retweet\ttopic_distribution\n')
file2.write('#author_id\tnum_retweet\ttopic_distribution\n')
author_topics_l1 = []
author_topics_l2 = []
for item in author:
	length = str(item[0])
	id = str(item[1])
	temp1 = calculate_l1(item[2:])
	temp2 = calculate_l2(item[2:])
	
	file1.write(id+'\t'+length)
	file2.write(id+'\t'+length)
	for each in temp1:
		file1.write('\t'+str(each))
	file1.write('\n')
	for each in temp2:
		file2.write('\t'+str(each))
	file2.write('\n')

file1.close()
file2.close()

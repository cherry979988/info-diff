#include <map>
#include <string>
#include <set>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
using namespace std;

const int monthbegin[] = {0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335};

class datetime {
public:
	int year;
	int month;
	int day;
	int hour;
	int minute;
	int second;
	bool operator < (datetime &d1) {
		if (year != d1.year)
			return year < d1.year ? true : false;
		if (month != d1.month)
			return month < d1.month ? true : false;
		if (day != d1.day)
			return day < d1.day ? true : false;
		if (hour != d1.hour)
			return hour < d1.hour ? true : false;
		if (minute != d1.minute)
			return minute < d1.minute ? true : false;
		if (second != d1.second)
			return second < d1.second ? true : false;
		return false;
	}
};

datetime parse_time(string& dt) {
	datetime d;
	sscanf(dt.c_str(), "%d-%d-%d-%d:%d:%d", &(d.year), &(d.month), &(d.day), &(d.hour), &(d.minute), &(d.second));
	return d;
}

int datespan(datetime &d1, datetime &d2) {
	return monthbegin[d2.month] + d2.day - monthbegin[d1.month] - d1.day;
}

const int N = 1800000;

int user_num = 0;
int old2new[N];
int num2idx[31];
int idx2num[7] = {2, 3, 4, 5, 10, 20, 30};
vector<int> folin[N];
map<int, int> circles[N];
map<int, int> repost[7];
map<int, int> norepost[7];

void load_ids() {

	for (int i = 2; i < 6; ++i)
		num2idx[i] = i - 2;
	for (int i = 6; i <= 10; ++i)
		num2idx[i] = 4;
	for (int i = 11; i <= 20; ++i)
		num2idx[i] = 5;
	for (int i = 21; i <= 30; ++i)
		num2idx[i] = 6;

	printf("load ids\n");
	for (int i = 0; i < N; ++i)
		old2new[i] = -1;
	FILE *f = fopen("Z:/weibo/repost2/source/users_idx.txt", "r");
	int id, linen = 0;
	while (fscanf(f, "%d", &id) > 0) {
	//	cout << id << endl;
		old2new[id] = user_num++;
	}
	fclose(f);
	int n = user_num;
	for (int i = 0; i < N; ++i)
		if (old2new[i] == -1)
			old2new[i] = n++;
	printf("load ids done\n");
}

void load_network() {
	printf("load network\n");
	FILE *f = fopen("Z:/weibo/repost2/source/network_idx.txt", "r");
	int id0, id1, time;
	int n = 0;
	while (fscanf(f, "%d %d %d\n", &id0, &id1, &time) > 0) {
		id0 = old2new[id0];
		id1 = old2new[id1];
		if (id0 < user_num || id1 < user_num)
			folin[id1].push_back(id0);
		n++;
		if (n % 1000000 == 0)
			printf("%d\n", n);
	}
	fclose(f);
	printf("network done\n");
}

void load_circles() {
	printf("load circles\n");
	ifstream cf("Z:/weibo/repost2/source/c++/get_block/get_block/blocksn2.txt");
	string line;
	int id0, id1, c, n = 0;
	while (getline(cf, line)) {
		istringstream is(line);
		is >> id0;
		id0 = old2new[id0];
		while (is >> id1 >> c) {
			id1 = old2new[id1];
			circles[id0][id1] = c;
		}
		if (++n % 1000 == 0)
			printf("%d\n", n);
	}
	cf.close();
	printf("circles done\n");
}

int count_circle(int id, vector<int> &v, int stop) {
	set<int> s;
	for (int i = 0; i < stop && i < v.size(); ++i)
		s.insert(circles[id][v[i]]);
	return s.size();
}

void stat_one(map<int, datetime> &rp, datetime &t0) {
	map<int, datetime>::iterator iter = rp.begin(), iter1;
	map<int, vector<int> > rpnids, norpnids;
	while (iter != rp.end()) {
		int id1 = iter->first;
		datetime &t1 = iter->second;
		vector<int> &in = folin[id1];
		for (int i = 0; i < in.size(); ++i) {
			int id2 = in[i];
			if (id2 < user_num) {
				iter1 = rp.find(id2);
				if (iter1 != rp.end()) {
					datetime &t2 = iter1->second;
					if (t1 < t2)
						rpnids[id2].push_back(id1);
				} else
					norpnids[id2].push_back(id1);
			}
		}
		iter++;
	}
	map<int, vector<int> >::iterator it = rpnids.begin();
	while (it != rpnids.end()) {
		int id0 = it->first;
		vector<int> &ids = it->second;
		int maxidx =0;
		if (ids.size() <= 30)
			maxidx = num2idx[ids.size()];
		else
			maxidx = 6;
		for (int i = 0; i < maxidx; ++i)
			norepost[i][count_circle(id0, ids, idx2num[i])]++;
		repost[maxidx][count_circle(id0, ids, ids.size())]++;
		it++;
	}
	it = norpnids.begin();
	while (it != norpnids.end()) {
		int id0 = it->first;
		vector<int> &ids = it->second;
		int maxidx = 0;
		if (ids.size() <= 30)
			maxidx = num2idx[ids.size()];
		else
			maxidx = 6;
		for (int i = 0; i <= maxidx; ++i)
			norepost[i][count_circle(id0, ids, idx2num[i])]++;
		it++;
	}
}

void output() {
	printf("output\n");
	int idx[] = {2, 3, 4, 5, 10, 20, 30};
	for (int i = 0; i < 7; ++i) {
		char name[100];
		sprintf(name, "prob_set_sizefix%d.txt", idx[i]);
		FILE *f = fopen(name, "w");
		map<int, int>::iterator iter = repost[i].begin();
		while (iter != repost[i].end()) {
			int n = iter->first;
			int r = iter->second;
			int nr = norepost[i][n];
			fprintf(f, "%d\t%d\t%d\t%f\n", n, r, nr, double(r) / (r + nr));
			++iter;
		}
		fclose(f);
	}
	printf("output done!\n");
}

void prob() {
	printf("prob\n");
	ifstream fin("Z:/weibo/repost2/source/total.txt");
	string line, t, mid;
	int n = 0, id, k = 0;
	char c;
	map<int, datetime> rp;
	datetime t0;
	while(getline(fin, line)) {
		istringstream is1(line);
		is1 >> mid >> t;
		k = 0;
		getline(fin, line);
		if (t >= "2012-00-00-00:00:00") {
			istringstream is2(line);
			rp.clear();
			while (is2 >> id >> t) {
				id = old2new[id];
				datetime t1 = parse_time(t);
				rp[id] = t1;
				if (k == 0)
					t0 = t1;
				k++;
			}
			stat_one(rp, t0);
		}
		printf("%d\n", n++);
		if (n % 1000 == 0)
			output();
	}
	fin.close();
	printf("prob done\n");
}

int main() {
	load_ids();
	load_network();
	load_circles();
	prob();
	output();
	return 0;
}

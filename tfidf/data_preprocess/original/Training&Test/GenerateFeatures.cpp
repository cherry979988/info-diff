#include <iostream>
#include <fstream>
#include <vector>
#include <math.h>
#include <map>
#include <sstream>
#include <stdlib.h>
#include <time.h>

using namespace std;

map<int, map<int, double> > sim;

void load_sim() {
	printf("load sim\n");
	FILE *simf = fopen("Z:/weibo/repost2/source/c++/GenerateTrainingFile/GenerateTrainingFile/weibo_network_rwr_10000_80.txt", "r");
	//FILE *simf = fopen("Z:/weibo/repost2/source/c++/GenerateTrainingFile/GenerateTrainingFile/network_sample.txt", "r");
	int m, n, id1, id2, tie;
	double sd, max = 0;
	fscanf(simf, "%d", &m);
	fscanf(simf, "%d", &n);
	n = 0;
	double simv[10000];
	int idsv[10000];
	while (fscanf(simf, "%d", &id1) >0) {
		if (++n % 1000 == 0)
			printf("%d\n", n);
		fscanf(simf, "%d", &m);
		max = 0;
		for (int i = 0; i < m; ++i) {
			fscanf(simf, "%d %d %lf", &id2, &tie, &sd);
			max = max > sd ? max : sd;
			simv[i] = sd;
			idsv[i] = id2;
		}
		map<int, double> &tmpmap = sim[id1];
		if (max != 0)
			for (int i = 0; i < m; ++i)
				tmpmap[idsv[i]] = simv[i] / max;
	}
	fclose(simf);
	printf("sim done\n");
}

//label(0) features(1-21)
#define N 22

int main() {
	srand((unsigned)time(NULL));
	load_sim();
	ifstream fin("Z:/weibo/repost2/source/c++/instance/instance/instances_sample.txt");
	string line;
	vector<vector<double> > ins;
	vector<double> max;
	vector<double> aver;
	for (int i = 0; i < N; ++i) {
		max.push_back(0);
		aver.push_back(0);
	}
	int xx = 0;
	int id0;
	while (getline(fin, line)) {
		if (++xx % 10000 == 0)
			cout << xx << endl;
		double tmpd;
		vector<double> vec;
		istringstream is(line);
		is >> id0;

		//label(0) & basic (1-8)
		for (int i = 0; i < 9; ++i) {
			is >> tmpd;
			vec.push_back(tmpd);
		}
		if (vec[8] > 72) {
			for (int i = 0; i < 5; ++i)
				getline(fin, line);
			continue;
		}
	
		map<int, double> &tmpmap = sim[id0];

		//friends' size(9-10)
		getline(fin, line);
		istringstream is0(line);
		is0 >> tmpd;
		vec.push_back(tmpd);
		vec.push_back(log(tmpd + 1));

		//circle(11-12)
		getline(fin, line);
		istringstream is1(line);
		is1 >> tmpd;
		vec.push_back(tmpd);
		vec.push_back(exp(-tmpd));
		
		tmpd = 0;
		//ids
		vector<int> idxv;
		getline(fin, line);
		istringstream is2(line);
		while (is2 >> tmpd)
			idxv.push_back(tmpd);

		//similarity
		vector<double> simv;
		for (int i = 0; i <idxv.size(); ++i)
			simv.push_back(tmpmap[idxv[i]]);

		tmpd = 0;
		//tie
		vector<double> tmpv;
		getline(fin, line);
		istringstream is3(line);
		while (is3 >> tmpd) 
			tmpv.push_back(tmpd);

		tmpd = 0;
		//time(13-14)
		vector<int> tv;
		getline(fin, line);
		istringstream is4(line);
		double s_aver = 0, j_aver = 1;
		while (is4 >>tmpd) {
			tv.push_back(tmpd);
			s_aver += tmpd;
			j_aver *= tmpd;
		}
		if (tv.size() != 0) {
			vec.push_back(s_aver / tv.size());
			vec.push_back(pow(j_aver, 1.0 / tv.size()));
		} else {
			vec.push_back(0);
			vec.push_back(0);
		}

		//sim(15-17)
		if (idxv.size() != 0) {
			s_aver = 0;
			j_aver = 1;
			for (int i = 0; i <idxv.size(); ++i) {
				s_aver += simv[i];
				j_aver *= simv[i];
			}
			vec.push_back(s_aver);
			vec.push_back(s_aver / idxv.size());
			if (j_aver > 0)
				vec.push_back(pow(j_aver, 1.0 / idxv.size()));
			else
				vec.push_back(0);
		} else {
			vec.push_back(0);
			vec.push_back(0);
			vec.push_back(0);
		}

		//time * sim(18-21)
		if (tv.size() != 0) {
			s_aver = 0;
			j_aver = 1;
			double mx = 0;
			for (int i = 0; i < tv.size(); ++i) {
				double d = tv[i] * simv[i];
				s_aver += d;
				j_aver *= d;
				mx = mx > d ? mx : d;
			}
			vec.push_back(s_aver);
			vec.push_back(s_aver / tv.size());
			if (j_aver > 0)
				vec.push_back(pow(j_aver, 1.0 / tv.size()));
			else
				vec.push_back(0);
			vec.push_back(mx);
		} else {
			vec.push_back(0);
			vec.push_back(0);
			vec.push_back(0);
			vec.push_back(0);
		}
		for (int i = 0; i < N; ++i) {
			if (vec[i] > max[i])
				max[i] = vec[i];
			aver[i] += vec[i];
		}
		ins.push_back(vec);
	}
	FILE *maxf = fopen("max.txt", "w");
	fprintf(maxf, "max:\n");
	for (int i = 1; i < N; ++i)
		fprintf(maxf, "%lf\n", max[i]);
	fprintf(maxf, "\naver:\n");
	for (int i = 1; i < N; ++i)
		fprintf(maxf, "%lf\n", aver[i] / ins.size());
	fclose(maxf);
	FILE *insf = fopen("ins.txt", "w");
	int one = 0;
	for (int i = 0; i < ins.size(); ++i) {
		if (ins[i][0] == 0) {
			if (one == 0)
				continue;
			one--;
		} else
			one++;
		for (int j = 0; j < N; ++j)
			fprintf(insf, "%lf ", ins[i][j] / max[j]);
		fprintf(insf, "\n");
	}
	fclose(insf);
}

#include "maxent.h"
#include "analyzer.h"

#include <utility>
#include <cstdio>
#include <string>
#include <vector>
#include <algorithm>
#include "Util.h"

#define MAX_BUF_SIZE 65536

using namespace std;

double absValue(double x) {
	if (x < 0)
		return -1 * x;
	return x;
}

bool cmp(pair<pair<int, int>, double> a, pair<pair<int, int>, double> b) {
	return a.second < b.second;
}

vector<string> StringSplit(string line, char separator) {
	vector<string> result;
	line += separator;

	int p = 0;
	for (unsigned int i = 0; i < line.length(); i++)
		if (line[i] == separator) {
			if (i - p >= 0)
				result.push_back(line.substr(p, i - p));
			p = i + 1;
		}

	return result;
}

int Analyzer::Analysis(int num, const char* outputDir) {
	vector<int> X;
	vector<int> Y;
	vector<int> Z;
	vector<int> W;
	int minValue = -1;
	int maxValue = 0;

	//	printf("sample size = %d\n", samples.size());
	for (unsigned int i = 0; i < samples.size(); i++) {
		//		printf(" feature value = %d\n", samples[i]->treatednum);
		if (samples[i]->treatednum > maxValue){
			maxValue = samples[i]->treatednum;
		}
		if (samples[i]->treatednum< minValue || minValue < 0)
			minValue = samples[i]->treatednum;

	}

	//int step = (maxValue - minValue) / num;
	int step = 1;
//	printf("minvalue = %d, maxvalue = %d, step = %d\n", minValue, maxValue, step);
	X.clear();
	Y.clear();
	Z.clear();
	W.clear();
	bool flag = false;
	for (int val = 1; val <= maxValue; val += step) {
		printf("=========current value = %d, maxValue = %d ===============\n", val, maxValue);
		pair<int, pair<int, int> > res = Analysis(val);
		//pair<int, pair<int, int> > res = CompareAnalysis(val);
		X.push_back(val);
		Y.push_back(res.first);
		Z.push_back(res.second.first);
		W.push_back(res.second.second);
	}
//	printf("==========write output to file=========\n");
	FILE* fout = fopen(outputDir, "a");
	for (unsigned int j = 0; j < X.size(); j++){
		//		printf("%d\t%d\t%d\t%d \t", X[j], Y[j], Z[j], W[j]);
		fprintf(fout, "%d\t%d\t%d\t%d\t\t", X[j], Y[j], Z[j], W[j]);
	}
	fprintf(fout, "\n");
	fclose(fout);
//	printf("write done!\n");

	return 0;
}

bool cmp2(pair<int, double> a, pair<int, double> b) {
	return a.second < b.second;
}


pair<int, pair<int, int> > Analyzer::Analysis(int val) {
	vector<pair<int, double> > treatList;
	vector<pair<int, double> > untreatList;
	ME_Model model;
	vector<ME_Sample> msamples;
	vector<int> adoptionLabels;
	int tn = 0;
	int un = 0;
//		printf("sample size = %d, val = %d\n", samples.size(), val);

	int index = 0;
	for (unsigned int i = 0; i < samples.size(); i++) {
		Sample* sample = samples[i];
		ME_Sample msample;
		if (sample->treatednum <= val) {
			msample.set_label("untreated");
			untreatList.push_back(make_pair(index,0.0));
			adoptionLabels.push_back(sample->adopted);
			for (unsigned int j = 0; j < sample->features.size(); j++) {
				msample.add_feature(Util::Int2Str(j), sample->features[j]);
			}
			model.add_training_sample(msample);
			msamples.push_back(msample);
			index ++;

			if(sample->adopted == 1)
				un ++;
		} else if (sample->treatednum > val) {
			msample.set_label("treated");
			treatList.push_back(make_pair(index,0.0));
			adoptionLabels.push_back(sample->adopted);

			for (unsigned int j = 0; j < sample->features.size(); j++) {
				msample.add_feature(Util::Int2Str(j), sample->features[j]);
			}
			model.add_training_sample(msample);
			msamples.push_back(msample);
			index++;

			if(sample->adopted == 1)
				tn++;
		}

	}
	printf("Treatednum = %d, Untreatednum = %d, treatedadopted = %d, untreatedadopted = %d, adoptednum = %d, undoptednum = %d\n", (int) treatList.size(),
			(int) untreatList.size(), tn, un, tn+un, treatList.size()+untreatList.size() - tn- un);
//	tn = 0; un = 0;
//	for(int i = 0 ; i < adoptionLabels.size() ; i++){
//		if(adoptionLabels[i] == 1) tn++;else un++;
//	}
//	printf("Labels, adoptednum = %d, unadopted = %d\n", tn, un);
	if (treatList.size() == 0 || untreatList.size() == 0) return make_pair(0, make_pair(0, 0));
	model.use_l2_regularizer(1.0);
	model.train();
	// calculate propensity score
	double* score = new double[msamples.size()];
	for (unsigned int i = 0; i < msamples.size(); i++) {
		//vector<double> P = model.classify(msamples[i]);
		score[i] = model.classify(msamples[i])[0];
//				printf("The %dth sample with score =  %lf\n", (int) i, score[i]);
	}
//	printf("Classify done, sample size = %d!\n", msamples.size());



//	bool* done = new bool[samples.size()];
//	memset(done, false, sizeof(done));



//	printf("set score to treated list\n");
	for (unsigned int i = 0; i < treatList.size(); i++) {
		int a = treatList[i].first;
		treatList[i].second = score[a];
//		printf("a= %d , tscore = %lf\n ",a, score[a]);
	}

//	printf("set score to untreated list\n");
	for (unsigned int i = 0; i < untreatList.size(); i++) {
		int a = untreatList[i].first;
		untreatList[i].second = score[a];
//		printf("a= %d , tscore = %lf\n ",a, score[a]);
	}



//	printf("sort begin\n");
	sort(treatList.begin(), treatList.end(), cmp2);
	sort(untreatList.begin(), untreatList.end(), cmp2);
	vector<pair<pair<int, int>, double> > compareList;

//	printf("sorted\n");

	int last_matched = 0;
	double last_diff = 2147483647;
	double mean = 0;
	for(int i = 0 ; i < treatList.size() ; i++){
		int a = treatList[i].first;
		double tscore = treatList[i].second;
//				printf("a= %d , tscore = %lf\n ",a, tscore);
		for(int j = last_matched ; j < untreatList.size() ; j++){
			int b = untreatList[j].first;
			double uscore = untreatList[j].second;
			double diff = absValue(uscore -  tscore);
//						printf("b= %d , uscore = %lf, diff = %lf, last_diff = %lf, last_matched = %d\n ",b, uscore, diff, last_diff, untreatList[last_matched].first);
			if(diff > last_diff ){
				compareList.push_back(make_pair(make_pair(a, untreatList[last_matched].first), last_diff));
				mean += last_diff;
				last_diff = 2147483647;
//				printf("select = %d \n ",untreatList[last_matched].first);
				last_matched++;
				break;
			}else if (j == untreatList.size() -1){
				compareList.push_back(make_pair(make_pair(a, untreatList[j].first), diff));
				last_diff = 2147483647;
				last_matched = untreatList.size() -1;
				mean += diff;
//				printf("select = %d \n ",untreatList[j].first);
			}else{
				last_diff = diff;
				last_matched = j;
			}
		}
	}



//	printf("matched done!\n");



	//	vector<pair<pair<int, int>, double> > pickList;
	//	/*
	//	 for (unsigned int i = 0; i < instanceList.size(); i ++)
	//	 printf("%.3lf ", score[i]);
	//	 printf("\n");
	//	 */
	//
	//	for (unsigned int i = 0; i < treatList.size(); i++) {
	//		int a = treatList[i];
	//		for (unsigned int j = 0; j < untreatList.size(); j++) {
	//			int b = untreatList[j];
	//			pickList.push_back(
	//					make_pair(make_pair(a, b), absValue(score[a] - score[b])));
	//		}
	//	}




	//	sort(pickList.begin(), pickList.end(), cmp);
	//	double mean = 0;
	//	vector<pair<pair<int, int>, double> > compareList;
	//	for (unsigned int i = 0; i < pickList.size(); i++) {
	//		int a = pickList[i].first.first;
	//		int b = pickList[i].first.second;
	//		double s = pickList[i].second;
	//		if (done[a] || done[b])
	//			continue;
	//		done[a] = true;
	//		done[b] = true;
	//		compareList.push_back(make_pair(make_pair(a, b), s));
	//		mean += s;
	////		printf("a = %d, b = %d, s = %lf\n", a, b, s);
	//	}
	mean =  mean / compareList.size();
	//	pickList.clear();
	double delta = 0;

	for (unsigned int i = 0; i < compareList.size(); i++) {
		//		printf("mean - element = %lf\n", mean - compareList[i].second);
		delta += (mean - compareList[i].second)
						* (mean - compareList[i].second);
	}
	int n1 = 0;
	int n2 = 0;
	int sampleNum = 0;
	for (unsigned int i = 0; i < compareList.size(); i++) {
		int a = compareList[i].first.first;
		int b = compareList[i].first.second;
		double s = compareList[i].second;
//				printf("a = %d, b=%d, score_a = %lf, score_b= %lf, s = %lf, s*s = %lf, delta= %lf, 4delta = %lf\n", a, b, score[a], score[b], s, s * s, delta, 4*delta);

		if (s * s <= 4 * delta)       // || sampleNum < compareList.size() / 5)
		{
			sampleNum++;
			n1 += adoptionLabels[a];
			n2 += adoptionLabels[b];
//			printf("seleted\n");
		}
	}
	delete[] score;
	printf("#Sample=%d,n1=%d,n2=%d\n ", sampleNum,n1, n2);
	return make_pair(sampleNum, make_pair(n1, n2));
}

pair<int,pair<int,int> > Analyzer::CompareAnalysis(double val) {
	vector<int> treatList;
	vector<int> untreatList;
	vector<int> adoptionLabels;
	int index = 0;
	for (unsigned int i = 0; i < samples.size(); i++) {
		if (samples[i]->treatednum == 1){
			untreatList.push_back(index);
			adoptionLabels.push_back(samples[i]->adopted);
			index ++;
		}else if (samples[i]->treatednum >= val ){
			treatList.push_back(index);
			adoptionLabels.push_back(samples[i]->adopted);
			index++;
		}
	}

	double n1 = 0;
	double n2 = 0;
	for (unsigned int i = 0; i < treatList.size() && i < untreatList.size();
			i++) {
		n1 += adoptionLabels[treatList[i]];
		n2 += adoptionLabels[untreatList[i]];
	}

	int sampleNum = treatList.size();
	if(sampleNum > untreatList.size()){
		sampleNum = untreatList.size();
	}
	printf("#Sample=%d,n1=%d,n2=%d\n ", sampleNum,n1, n2);
	return make_pair(sampleNum, make_pair(n1, n2));
}


void Analyzer::Analysis(const char* fileDir, const char* outputDir) {
	char buf[MAX_BUF_SIZE];
	char* eof;
	string line;
	FILE* fin = fopen(fileDir, "r");

	while (true) {
		samples.clear();
		eof = fgets(buf, MAX_BUF_SIZE, fin);
		//		printf("current line = %s\n", eof);
		while (eof != NULL && eof[0] != '#') {
			eof = fgets(buf, MAX_BUF_SIZE, fin);
			printf("current line = %s\n", eof);
			string line = eof;
			vector<string> strs = Util::StringSplit(line,' ');

			Sample* sample = new Sample();

			int adoptive = Util::String2Int(strs[0]);
			sample->adopted = adoptive;
			int treated = Util::String2Int(strs[1]);
			sample->treatednum = treated;
			for (unsigned int i = 2; i < strs.size(); i++) {
				string value = strs[i];
				double v = 0;
				bool flag = true;
				double p = 0.1;
				for (unsigned int j = 0; j < value.length(); j++) {
					if (value[j] >= '0' && value[j] <= '9') {
						if (flag)
							v = v * 10 + value[j] - '0';
						else {
							v = v + (value[j] - '0') * p;
							p *= 0.1;
						}
					} else
						flag = false;
				}
				sample->AddFeature(v);
			}
			//printf("sample = %s\n", sample->toString().c_str());
			samples.push_back(sample);
		}

		Analysis(1, outputDir);
		printf("#Instance: %d\n", (int) samples.size());
		printf("#Features: %d\n", (int) samples[0]->features.size());

		if (eof == NULL)
			break;
		repostnum++;
		printf("repost number = %d\n", repostnum);
	}
	fclose(fin);
}



/*
void Analyzer::Analysis(const char* fileDir, const char* outputDir) {
	char buf[MAX_BUF_SIZE];
	char* eof;
	string line;
	FILE* fin = fopen(fileDir, "r");

	while (true) {
		samples.clear();
		eof = fgets(buf, MAX_BUF_SIZE, fin);
//		printf("current line = %s\n", eof);
		while (eof != NULL && eof[0] != '#') {
			eof = fgets(buf, MAX_BUF_SIZE, fin);
			printf("current line = %s\n", eof);
			string line = eof;
			vector<string> strs = Util::StringSplit(line,' ');

			Sample* sample = new Sample();

			int adoptive = Util::String2Int(strs[0]);
			sample->adopted = adoptive;
			int treated = Util::String2Int(strs[1]);
			sample->treatednum = treated;
			for (unsigned int i = 2; i < strs.size(); i++) {
				string value = strs[i];
				double v = 0;
				bool flag = true;
				double p = 0.1;
				for (unsigned int j = 0; j < value.length(); j++) {
					if (value[j] >= '0' && value[j] <= '9') {
						if (flag)
							v = v * 10 + value[j] - '0';
						else {
							v = v + (value[j] - '0') * p;
							p *= 0.1;
						}
					} else
						flag = false;
				}
				sample->AddFeature(v);
			}
			//printf("sample = %s\n", sample->toString().c_str());
			samples.push_back(sample);
		}

		Analysis(1, outputDir);
		printf("#Instance: %d\n", (int) samples.size());
		printf("#Features: %d\n", (int) samples[0]->features.size());

		if (eof == NULL)
			break;
		repostnum++;
		printf("repost number = %d\n", repostnum);
	}
	fclose(fin);
}

 */

Sample::Sample() {
	features.clear();
	this->treatednum = 0;
	this->adopted = 0;
}
void Sample::AddFeature(double value) {
	features.push_back(value);
}

string Sample::toString(){
	string str = Util::Int2Str(this->adopted)+" "+Util::Int2Str(this->treatednum);
	for(int i = 0 ; i < this->features.size() ; i++){
		str = str + " "+Util::Double2Str(this->features[i]);
	}
	return str;
}

void Analyzer::deleteSamples(){
	for(int i = 0 ; i < samples.size() ; i ++){
		delete samples[i];
	}
	samples.clear();
}


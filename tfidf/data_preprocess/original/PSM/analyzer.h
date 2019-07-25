#ifndef __ANALYZER_H_
#define __ANALYZER_H_

#include <cstring>
#include <string>
#include <vector>

using namespace std;


class Sample {
public:
	int adopted;
	int treatednum;
	vector<double> features;

	Sample();
	void AddFeature(double value);
	string toString();

};

class Analyzer {
public:
	int repostnum;
	vector<Sample*> samples;

	Analyzer(){
		repostnum = 0;
	}
	void Analysis(const char* fileDir, const char* outputDir);
	pair<int, pair<int,int> > Analysis( int val);
	pair<int,pair<int,int> >  CompareAnalysis(double val);
	int Analysis(int num, const char* outputDir);
	void deleteSamples();
};



#endif


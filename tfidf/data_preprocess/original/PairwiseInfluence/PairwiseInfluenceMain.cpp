// to draw a curve of the probability changing over the number of circles while fixing the size and the time.
// here, we fix the time in the first day, and fix the friends size to 2, 3, 4, 5, 6-10, 11-20, 21-30

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
#include <cstdio>
#include <set>
#include <algorithm>
#include "Util.h"
#include "NetworkData.h"


using namespace std;

// which day in a year(2012) is the beginning of a month ?
const int monthbegin[] = { 0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305,
		335 };

char *network_file;
char *adoption_file;
string outputpath;



class datetime {
public:
	int year;
	int month;
	int day;
	int hour;
	int minute;
	int second;
	// compare two date
	bool operator <(datetime &d1) {
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

	string toString() {
		string s = Util::Int2Str(year) + "-" + Util::Int2Str(month) + "-"
				+ Util::Int2Str(day) + "-" + Util::Int2Str(hour) + ":"
				+ Util::Int2Str(minute) + ":" + Util::Int2Str(second);
		return s;
	}
};

// convert the time expressed by string to datetime.
datetime parse_time(string& dt) {
	datetime d;
	sscanf(dt.c_str(), "%d-%d-%d-%d:%d:%d", &(d.year), &(d.month), &(d.day),
			&(d.hour), &(d.minute), &(d.second));
	return d;
}

// to calculate the span between to date d1 and d2.
int datespan(datetime &d1, datetime &d2) {
	return monthbegin[d2.month] + d2.day - monthbegin[d1.month] - d1.day;
}

int hourspan(datetime &d1, datetime &d2) {
	return d2.hour - d1.hour;
}



// time difference from time1 to time2, time2 > time1
int get_time_diff(datetime time1, datetime time2) {
	int date_diff = datespan(time1, time2);
	//	printf("date diff is calculated as %d\n", date_diff);
	int hour_diff = hourspan(time1, time2);
	//	printf("hour diff is calculated as %d\n", hour_diff);
	int time_diff = date_diff * 24 + hour_diff ;
	return time_diff;
}

const int N = 1800000;

// the number of users we selected.
int user_num = 0;
// the users' followers
//vector<int> folin[N];
// the number of users who reposted the root blog with a number of specified circles and specified file index.
map<int, int> repost[2];
// the number of users who didn't repost the root blog with a number of specified circles and specified file index.
map<int, int> norepost[2];
NetworkData network;


// load the network of the users we selected, 
void load_network() {
	printf("load network\n");

	network.ReadNetwork(network_file);
	printf("network done\n");

}

//void randomWalkWithRestart(){
//	int N = 4;
//	int subnodes[N];
//	for(int i = 0 ; i < N ; i++){
//		subnodes[i] = i+10;
//	}
//
//
//	vector<int> subnetwork[N];
//	subnetwork[0].push_back(1);
//	subnetwork[0].push_back(2);
//	subnetwork[1].push_back(0);
//	subnetwork[2].push_back(1);
//	subnetwork[2].push_back(0);
//	subnetwork[0].push_back(3);
//
//	double page_rank[N];
//	page_rank[0] = 1;
//	for (int i=1;i<N;i++) page_rank[i]=0;
//
//
//	double *s=new double[N];
//	double ratio = 0.85;
//	for( int step = 0 ; step < 5 ; step ++){
////		printf("=====step = %d\n", step);
//		for(int i = 0 ; i < N ; i++ ){
////			printf("=====node i  = %d\n", i);
//			for (int j = 0 ; j < subnetwork[i].size() ; j++){
//				int out_index = subnetwork[i][j];
//				s[out_index]+=ratio*page_rank[i]/subnetwork[i].size();
////				printf("j= %d, page_rank[i] =%lf, s[j] = %lf\n",  out_index, page_rank[i], s[out_index]);
//			}
//		}
//		double maxp=0;
//		s[0] += 1- ratio;
//		for(int i = 0 ; i <  N ; i++){
//			page_rank[i] = s[i];
//			s[i] = 0;
//			if (page_rank[i]>maxp) maxp=page_rank[i];
////			printf("i= %d, pagerank = %f\n",  i, page_rank[i]);
//		}
//
////		printf("After normalization \n");
//		//if (maxp<1e-10) break;
//		for (int i=0;i<N;i++){
//			page_rank[i]/=maxp;
//			printf("i= %d, pagerank = %f\n",  i, page_rank[i]);
//		}
//	}
//
//	delete[] s;
//
//}





void printNetwork() {

	vector<int>::iterator sit;
	for (int i = 0; i < network.nodenum; i++) {
		printf("%d ", i);

		Edge* edge;
		for (int j = 0; j < network.edge_to_list[i].size(); ++j) {
			edge = network.edge_to_list[i][j];
			printf("source = %d, target = %d,  ", edge->v1, edge->v2);

		}
		printf("\n");
	}
}



int timestamps[6];

void init_timestamps() {
	timestamps[0] = 1;
	timestamps[1] = 5;
	timestamps[2] = 10;
	timestamps[3] = 24;
	timestamps[4] = 48;
	timestamps[5] = 72;
}



int find_feature_file(datetime root_time, datetime re_time) {
	int f = 0;
	int date_diff = datespan(root_time, re_time);
	//	printf("date diff is calculated as %d\n", date_diff);
	int hour_diff = hourspan(root_time, re_time);
	//	printf("hour diff is calculated as %d\n", hour_diff);
	int time_diff;
	if (hour_diff < 0) {
		time_diff = (date_diff - 1) * 24 + hour_diff + 24;
	} else {
		time_diff = date_diff * 24 + hour_diff;
	}
	//	printf("time diff is calculated as %d\n", time_diff);
	for (int i = 0; i < 6; i++) {
		//		printf("timestamps is  %d\n", timestamps[i]);
		if (time_diff < timestamps[i]) {
			return i;
		}
	}
	return 5;
}

int dividesum(double number){
	int f = -1;
	int size = 65;
	int i = 1;
	int index = 0;
	while (i <= size){
		if(number <= i){
			f = index;
			break;
		}
		index++;
		i = i+2;
	}
	return f;
}

int divideave(double number){
	int f = -1;
	double size = 1.2;
	double i = 0.05;

	int index = 0;
	while (i <= size){
		//printf("number = %lf, i = %lf, index =%d\n", number, i, index);
		if(number <= i){
			f = index;
			break;
		}
		index++;
		i = i+0.05;
	}
	return f;
}



int current_post_num = 0;
int output_index = 0;

//statistics in one repost list
//@param rid is the root user id
//@param rmid is the root message id
//@param rp is a repost list
//@param t0 is the time the root blog reposted.

double max_sum = 0;
double max_ave = 0;

void stat_one(int rid, string rmid, int post_num, map<int, datetime> &rp,
		datetime &t0) {
	printf("=====post i = %d\n", current_post_num++);

	map<int, datetime>::iterator iter = rp.begin(), iter1;
	//rpnids saves a user's friends who reposted the root blog before him, the user reposted the blog.
	//norpnids saves all of the user's friends who reposted the root blog, the user didn't repost the blog
	map<int, vector<int> > rpnids, norpnids;
	map<int, vector<datetime> > rpntime, norpntime;
	// record the instances and its own retweet time
	map<int, datetime> rtime;
	map<int, datetime>::iterator rtimeit;
	map<int, vector<double> > rpsim, norpsim;

	int i = 0;
	while (iter != rp.end()) {
		// a user's id
		int id1 = iter->first;
		// the time he reposted the blog
		datetime &t1 = iter->second;
		//		printf("rid:%d r_mid:%s, r_t:%s ",rid, rmid.c_str(), t0.toString().c_str());

		//				printf("c_u:%d c_t:%s ", id1, t1.toString().c_str());
		if(t1 < t0) {
			iter++;
			continue;
		} // discard the retweeter whose time is earlier than the root

		rtimeit = rtime.find(id1);
		if (rtimeit == rtime.end()) {
			rpnids[id1];
			rpntime[id1];
			rtime[id1] = t1;
		}



		// check all of his followers
		for (int k = 0 ; k < network.edge_to_list[id1].size(); k ++) {
			// one of his follower
			Edge* edge = network.edge_to_list[id1][k];
			int id2 = edge->v1;
			// id2 is selected
			//if (id2 < user_num) {
			iter1 = rp.find(id2);
			//id2 reposted the blog
			//						printf("f_u:%d ", id2);

			if (iter1 != rp.end()) {
				datetime &t2 = iter1->second;
				//								printf("c_t:%s ", t2.toString().c_str());

				if (t1 < t2) {
					//										printf("%d < %d", id1, id2);
					// save the user who repost the root blog before him
					rpnids[id2].push_back(id1);
					rpntime[id2].push_back(t1);
					rpsim[id2].push_back(edge->sim);
					rtime[id2] = t2;
				}
			} else {
				//								printf(" not do!");

				//id2 didn't repost the blogx
				norpnids[id2].push_back(id1);
				norpntime[id2].push_back(t1);
				norpsim[id2].push_back(edge->sim);
				rtime[id2] = t0; // temporally set the time as root time
			}
			//						printf("\\");
			//}
		}

		//				printf("\n");
		iter++;
	}

//	printf("===========positive instance============\n");
	map<int, vector<int> >::iterator outit;
	for (outit = rpnids.begin(); outit != rpnids.end(); outit++) {
		int uid = outit->first;
//		printf("uid = %d\n", uid);
		vector<int>& re_followees = outit->second;
		if (re_followees.size() == 0) continue;
		vector<datetime>& re_followee_times = rpntime[uid];
//		printf("followee time size = %d\n", re_followee_times.size());
		datetime t2 = rtime[uid];
		int f_index = find_feature_file(t0, t2);
		//printf("f index = %d\n", f_index);
		vector<double>& sims = rpsim[uid];
		for (int i = 0; i <= f_index; i++) {
			double ave = 0;
			double sum = 0;
			int followee_size = 0;
			for (int j = 0; j < re_followee_times.size(); j++) {
				datetime re_followee_time = re_followee_times[j];
				int time_diff = get_time_diff(t0, re_followee_time);
				double sim = 0;
				if (time_diff < timestamps[i]) {
					sim = sims[j];
					sum +=sim;
					followee_size++;
				}
//				printf("fid = %d, sim =%lf, ave = %lf, sum=%lf\n", re_followees[j], sim, ave, sum);
			}
			ave = sum/followee_size;

			if(max_sum < sum ) max_sum = sum;
			if(max_ave < ave) max_ave = ave;

			int f_avg = divideave(ave);
			if(f_avg == -1) continue;
			int f_sum = dividesum(sum);
			if(f_sum == -1) continue;
//			printf("ave = %lf,sum = %lf, f_max = %d, f_avg= %d\n ", ave, sum, f_avg, f_sum );
			if(i == f_index){
//				printf("=== positive instance \n");
				repost[0][f_avg] ++;
				repost[1][f_sum] ++;
			}else{
//				printf("=== negative instance \n");
				norepost[0][f_avg] ++;
				norepost[1][f_sum] ++;
			}
		}

	}

//		printf("===========negative instance============\n");

	// negative instances
	for (outit = norpnids.begin(); outit != norpnids.end(); outit++) {

		int uid = outit->first;
//		printf("uid = %d\n", uid);
		vector<int> re_followees = outit->second;
		if (re_followees.size() == 0) continue;
		vector<datetime>& re_followee_times = norpntime[uid];
		vector<double>& sims = norpsim[uid];

		for (int i = 0; i < 6; i++) {
			double ave = 0;
			double sum = 0;
			int followee_size = 0;

			for (int j = 0; j < re_followee_times.size(); j++) {
				datetime re_followee_time = re_followee_times[j];
				int time_diff = get_time_diff(t0, re_followee_time);
				double sim = 0;
				if (time_diff < timestamps[i]) {
					sim = sims[j];
					sum +=sim;
					followee_size ++;

				}
//				printf("fid = %d, sim =%lf,sum=%lf, followee_size = %d\n", re_followees[j], sim,  sum, followee_size);
			}
			if(followee_size == 0) continue;

			ave = sum/ followee_size;
			if(max_sum < sum ) max_sum = sum;
			if(max_ave < ave) max_ave = ave;

//			printf("ave = %lf,sum = %lf\n ", ave, sum);

			int f_avg = divideave(ave);
//			printf("f_avg = %d\n ", f_avg);
			if(f_avg == -1 ) continue;
			int f_sum = dividesum(sum);
//			printf("f_sum= %d\n ", f_sum );

			if(f_sum == -1) continue;


			norepost[0][f_avg] ++;
			norepost[1][f_sum] ++;
		}
	}
}

void output() {
		printf("output\n");

	char outputfile[200];
//	sprintf(outputfile, "%sstatsim.txt", outputpath.c_str());
//			//		printf("file = %s\n", outputfile);
//			FILE *f = fopen(outputfile, "w");
//	fprintf(f, "max sum = %lf, max ave = %lf\n", max_sum, max_ave);
//	fclose(f);
	//printf("path = %s\n", outputpath.c_str());
	for (int i = 0; i < 2; ++i) {
		sprintf(outputfile, "%stiesim-%d.txt", outputpath.c_str(), i);
		//		printf("file = %s\n", outputfile);
		FILE *f = fopen(outputfile, "w");
		map<int, int>::iterator it = repost[i].begin();
		while (it != repost[i].end()) {
			int n = it->first;
			int r = it->second;
			int nr = norepost[i][n];
			//			printf("%d\t%d\t%d\t%f\n", n, r, nr, double(r) / (r + nr));
			fprintf(f, "%d\t%d\t%d\t%f\n", n, r, nr, double(r) / (r + nr));
			it++;
		}
		fclose(f);
	}


	//	printf("output done!\n");
}



//statistics
void prob() {
	//	printf("prob\n");
	//'total.txt' contains the repost lists of all root blogs.
	// format:
	// rootmessageid roottime rootuserid repost_number
	// repostuserid reposttime retweetmessageid
	ifstream fin(adoption_file);
	string line, t, mid;
	int n = 0, id, k = 0, rid, post_num;
	char c;
	map<int, datetime> rp;
	map<int, datetime>::iterator irp;
	datetime t0;
	while (getline(fin, line)) {
		istringstream is1(line);
		is1 >> mid >> t >> rid >> post_num;
		k = 0;
		getline(fin, line);
		if (t >= "2012-00-00-00:00:00") {
			//printf("mid = %s time = %s, root id = %d\n", mid.c_str(), t.c_str(), rid);

			t0 = parse_time(t);
			istringstream is2(line);
			rp.clear();
			// parse a repost list
			while (is2 >> id >> t ) {
				//id = old2new[id];
				datetime t1 = parse_time(t);
				irp = rp.find(id);
				if (irp == rp.end()) {
					rp[id] = t1;
				}
				//				if (k == 0)
				//					t0 = t1;
				//				k++;
			}
			//printf("=reteet id = %d time = %s\n", id, t.c_str());
			stat_one(rid, mid, post_num, rp, t0);
		}
		if (n % 1000 == 0){
			printf("%d\n", n);
			output();
		}

		n++;
	}

	fin.close();
	printf("prob done\n");
}





void setDefault() {
	network_file =
			"/Users/zhangjing0544/Dropbox/workspace4c/Retweet/src/network_sample.txt";
	adoption_file =
			"/Users/zhangjing0544/Dropbox/workspace4c/Retweet/src/adoptions.txt";

	init_timestamps();

}
int loadConfig(int argc, char* argv[]) {
	if (argc < 4)
		return 0;
	int i = 1;
	while (i < argc) {
		if (strcmp(argv[i], "-g") == 0)  // required
		{
			network_file = argv[++i];
			++i;
		} else if (strcmp(argv[i], "-a") == 0)  // required
		{
			adoption_file = argv[++i];
			++i;
		} else if (strcmp(argv[i], "-o") == 0)  // required
		{
			char* outputpathchar = argv[++i];
			outputpath = outputpathchar;
			if(outputpath.at(outputpath.length()-1) != '/'){
				outputpath = outputpath + "/";
			}
			//			printf("outputpath = %s\n", outputpath.c_str());
			++i;
		}else
			++i;
	}
	return 1;
}

void showUsage() {
	printf("Usage: run -g NETWORKFILE -a ADOPTIONFILE -o OUTPUTPATH\n");
	printf(" Options:                                                    \n");
	exit(0);
}


// stat retweet probability when varying the average pairwise influence and sum pairwise influence from the followees

int main(int argc, char* argv[]) {
	setDefault();
	printf("set default value for parameters done\n");
	if (!loadConfig(argc, argv)) {
		showUsage();
		exit(0);
	}
	printf("load configuration done\n");
	load_network();
	prob();

	return 0;
}

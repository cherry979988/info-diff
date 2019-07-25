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
#include <time.h>
#include <math.h>
#include <stdio.h>
#include "Util.h"
#include "NetworkData.h"


using namespace std;

// which day in a year(2012) is the beginning of a month ?
const int monthbegin[] = { 0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305,
		335 };

char network_file[1000];
char adoption_file[1000];
char user_profile[1000];
char user_profile2[1000];
char usermapfile[1000];
string outputpath;
FILE *insf = NULL;

int max_bi_followers_count = 0;
int max_followers_count = 0;
int max_followee_count = 0;
int max_tweet_count = 0;
int max_post_num = 0;

int delta; //

vector<double> userch[1800000];
map<string, vector<double> > blogch;

map<int, int> circles[1800000];
int selected[1800000];

map<int, int> usermap;

void load_selected() {
	cout << "load_selected" << endl;
	FILE *f = fopen("Z:/weibo/repost2/source/users_idx.txt", "r");
	int uid;
	while (fscanf(f, "%d", &uid) > 0)
		selected[uid] = 1;
	fclose(f);
	cout << "load_selected done" << endl;
}

void load_ch() {
	cout << "doc" << endl;
	ifstream fin("D:/Users/tc/topic-100/doc");
	string line, mid;
	int id, idx;
	double weight;
	getline(fin, line);
	//cout << line << endl;
	//system("pause");
	while (getline(fin, line)) {
		istringstream is(line);
		is >> id >> mid;
		vector<double> &v = blogch[mid];
		v.resize(100);
		while (is >> idx >> weight)
			v[idx] = weight;

	}
	fin.close();
	cout << "doc done" << endl;
	cout << "author-topic-l2.txt" << endl;
	FILE *f = fopen("D:/Users/tc/topic-100/author-topic-l1.txt", "r");
	char cs[1000];
	fgets(cs, 1000, f);
	int uid, num;
	while (fscanf(f, "%d", &uid) > 0) {
		uid = usermap[uid];
		fscanf(f, "%d", &num);
		//printf("%d ", uid);
		vector<double> &v = userch[uid];
		for (int i = 0; i < 100; ++i) {
			//printf("%lf ", weight);
			fscanf(f, "%lf", &weight);
			v.push_back(weight);
		}
		//cout << "usize = " << userch[uid].size() << endl;
	//	system("pause");
		//printf("\n");
	}
	fclose(f);
	cout << "author-topic-l2.txt done" << endl;
}

class user {
public:
	int uid ;
	int bi_followers_count;
	int city;
	int verified ;
	int followers_count ;
	string location ;
	int province ;
	int followee_count ;
	string name;
	int gender ;
	int tweet_count ;
	string created_at;
	string verified_type;
	string description;

	user(){
		this->uid = -1;
		this->bi_followers_count = 0;
		this->city = 0;
		this->verified = 0;
		this->followers_count = 0;
		this->location = "";
		this->province = 0;
		this->followee_count = 0;
		this->name ="";
		this->gender = 0;
		this->tweet_count = 0;
		this->created_at ="";
		this->verified_type ="";
		this->description = "";
	}

	user(int uid){
		this->uid = uid;
		this->bi_followers_count = 0;
		this->city = 0;
		this->verified = 0;
		this->followers_count = 0;
		this->location = "";
		this->province = 0;
		this->followee_count = 0;
		this->name ="";
		this->gender = 0;
		this->tweet_count = 0;
		this->created_at ="";
		this->verified_type ="";
		this->description = "";
	}


	void setUid(int uid) {
		this->uid = uid;
	}
	int getUid() {
		return this->uid;
	}
	void setBiFollowerCount(int bi_followers_count) {
		this->bi_followers_count = bi_followers_count;
	}
	int getBiFollowerCount() {
		return this->bi_followers_count;
	}
	void setCity(int city) {
		this->city = city;
	}
	int getCity() {
		return this->city;
	}
	void setVerified(string verified) {
		if (verified.at(0) == 'F') {
			this->verified = 0;
		} else if (verified.at(0) == 'T') {
			this->verified = 1;
		}
	}
	int getVerified() {
		return this->verified;
	}
	void setFollowerCount(int followerCount) {
		this->followers_count = followerCount;
	}
	int getFollowerCount() {
		return this->followers_count;
	}
	void setLocation(string location) {
		//printf("location=%s\n", location.c_str());
		this->location = location;
	}
	string getLocation() {
		return this->location;
	}
	void setProvince(int province) {
		//printf("province=%d\n", province);
		this->province = province;
	}
	int getProvince() {
		return this->province;
	}

	void setFolloweeCount(int followee_count) {
		this->followee_count = followee_count;
	}
	int getFolloweeCount() {
		return this->followee_count;
	}
	void setName(string name) {
		this->name = name;
	}
	string getName() {
		return this->name;
	}
	void setGender(string gender) {
		if (gender.at(0) == 'm') {
			this->gender = 0;
		} else if (gender.at(0) == 'f') {
			this->gender = 1;
		}
	}
	int getGender() {
		return this->gender;
	}

	void setTweetCount(int tweet_count) {
		this->tweet_count = tweet_count;
	}

	int getTweetCount() {
		return this->tweet_count;
	}
	void setCreatedAt(string created_at) {
		this->created_at = created_at;
	}

	void setVerifiedType(string verified_type) {
		this->verified_type = verified_type;
	}
	void setDescription(string description) {
		this->description = description;
	}

	void print(){
		string result = "userid:"+Util::Int2Str(uid)+" bi_follower_count:"+Util::Int2Str(bi_followers_count)+" city:"+Util::Int2Str(city)+" verified:"+Util::Int2Str(verified)+
				" follower_count:"+Util::Int2Str(followers_count)+" location:"+location+" province:"+Util::Int2Str(province);
		+" followee_count:"+Util::Int2Str(followee_count)+
				" name:"+name+" gender:"+Util::Int2Str(gender)+" tweet_count:"+Util::Int2Str(tweet_count);
		printf(" userid = %d,  bi_follower_count = %d, city = %d, verified = %d, follower_count=%d,  province=%d, followee_count=%d, gender=%d, tweet_count=%d\n", uid, bi_followers_count, city, verified, followers_count, province, followee_count, gender, tweet_count);
	}

};



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
int daydiff(datetime &d1, datetime &d2) {
	return monthbegin[d2.month] + d2.day - monthbegin[d1.month] - d1.day;
}

int hourdiff(datetime &d1, datetime &d2) {
	return d2.hour - d1.hour;
}

int hour(datetime &d1, datetime &d2) {
	int d = daydiff(d1, d2);
	int h = hourdiff(d1, d2);
	if (d < 0)
		return 0;
	else
		return d * 24 + h;
}
const int N = 1800000;

// the number of users we selected.
int user_num = 0;

user users[N];



NetworkData network;


// load the network of the users we selected, 
void load_network() {
	printf("load network\n");
	network.ReadNetwork(network_file);
	printf("network done\n");

}

void load_user_map() {
	printf("load user map 1\n");
	//format: id0 id1 time
	FILE *f = fopen(usermapfile, "r");
	int userid;
	int n = 0;
	while (fscanf(f, "%d\n", &userid) > 0) {
		//		printf("userid = %d\n", userid);
		usermap[userid] = n;
		n++;
		if (n % 1000000 == 0)
			printf("%d\n", n);
	}
	fclose(f);
	printf("load user map done\n");

}

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

// sort a repost list by repost time.
// it is not efficient, but is easy enough
void sort(vector<int> &ids, vector<int> &tie, vector<datetime> &ts) {
	for (int i = 0; i < ids.size(); ++i) {
		for (int j = i + 1; j < ids.size(); ++j) {
			if (ts[j] < ts[i]) {
				int id = ids[i];
				ids[i] = ids[j];
				ids[j] = id;
				datetime t = ts[i];
				ts[i] = ts[j];
				ts[j] = t;
				int tt = tie[i];
				tie[i] = tie[j];
				tie[j] = tt;
			}
		}
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
	int date_diff = daydiff(root_time, re_time);
	//	printf("date diff is calculated as %d\n", date_diff);
	int hour_diff = hourdiff(root_time, re_time);
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


double dist(vector<double> &v1, vector<double> &v2) {
	double res1 = 0, res2 = 0;
	for (int i = 0; i < v1.size(); ++i) {
		double m = (v1[i] + v2[i]) / 2;
		if (m != 0) {
			if (v1[i] != 0)
				res1 += v1[i] * log(v1[i] / m);
			if (v2[i] != 0)
				res2 += v2[i] * log(v2[i] / m);
		}
	}
	return (res1 + res2) / 2;
}


void load_circles() {
	printf("load circles\n");
	ifstream cf("Z:/weibo/repost2/source/c++/get_block/get_block/blocksn2.txt");
	string line;
	int id0, id1, c, n = 0;
	while (getline(cf, line)) {
		istringstream is(line);
		is >> id0;
		while (is >> id1 >> c)
			circles[id0][id1] = c;
		if (++n % 1000 == 0)
			printf("%d\n", n);
	}
	cf.close();
	printf("circles done\n");
}


int count_circle(int id, vector<int> &v, int stop) {
	set<int> s;
	for (int i = 0; i < stop; ++i)
		s.insert(circles[id][v[i]]);
	return s.size();
}


int current_post_num = 0;
int output_index = 0;
//statistics in one repost list
//@param rid is the root user id
//@param rmid is the root message id
//@param rp is a repost list
//@param t0 is the time the root blog reposted.

void stat_one(int rid, string rmid, int post_num, map<int, datetime> &rp, datetime &t0) {
	printf("=====post i = %d\n", current_post_num++);

	vector<double> &mch = blogch[rmid];
	if (mch.size() != 100) {
		printf("mch_size = %d\n", mch.size());
		return;
	}

	if(max_post_num < post_num) max_post_num = post_num;
	map<int, datetime>::iterator iter = rp.begin(), iter1;
	map<int, vector<int> > rpnids, norpnids;
	map<int, vector<int> > rpntype, norpntype;
	map<int, vector<datetime> > rpntime, norpntime;

	//printf("x1\n");
	while (iter != rp.end()) {
		int id1 = iter->first;
		datetime &t1 = iter->second;
		if(t1 < t0) {
			iter++;
			continue;
		}
		rpnids[id1];
		rpntime[id1];
		rpntype[id1];

		for (int k = 0 ; k < network.edge_to_list[id1].size(); k ++) {
			Edge* edge = network.edge_to_list[id1][k];
			int id2 = edge->v1;
			iter1 = rp.find(id2);
			if (iter1 != rp.end()) {
				datetime &t2 = iter1->second;
				if (t1 < t2) {
					rpnids[id2].push_back(id1);
					rpntime[id2].push_back(t1);
					rpntype[id2].push_back(edge->type);
				}
			} else {
				norpnids[id2].push_back(id1);
				norpntime[id2].push_back(t1);
				norpntype[id2].push_back(edge->type);
			}
		}
		iter++;
	}

	map<int, vector<int> >::iterator it = rpnids.begin();
	
	while (it != rpnids.end()) {
		int uid = it->first;
		vector<double> &uch = userch[uid];
		if (selected[uid] && uch.size() == 100) {
			//printf("y2\n");
			datetime &dt = rp[uid];
			vector<int> &ids = it->second;
			vector<datetime> &ts = rpntime[uid];
			vector<int> &tie = rpntype[uid];
			//		sort(ids, ts);
			user& u = users[uid];
			
			fprintf(insf, "%d 1 %d %d %d %d %d %d ", uid, u.bi_followers_count , u.followers_count ,u.followee_count,
					u.tweet_count, u.gender, u.verified);
			
			fprintf(insf, "%lf %d\n", dist(mch, uch), hour(t0, dt)); 
			fprintf(insf, "%d\n", ids.size());
			//printf("z2\n");
			fprintf(insf, "%d\n", count_circle(uid, ids, ids.size()));
			//printf("y4\n");
			for (int i = 0; i < ids.size(); ++i)
				fprintf(insf, "%d ", ids[i]);
			fprintf(insf, "\n");
			for (int i = 0; i < tie.size(); ++i)
				fprintf(insf, "%d ", tie[i]);
			fprintf(insf, "\n");
			//printf("y5\n");
			for (int i = 0; i < ts.size(); ++i)
				fprintf(insf, "%d ", hour(ts[i], dt));
			fprintf(insf, "\n");
		//	printf("y6\n");
		}
		it++;
	}
	//printf("x3\n");
	it = norpnids.begin();
	int hours[] = {1, 5, 10, 24, 48, 72};
	while (it != norpnids.end()) {
		int uid = it->first;
		vector<double> &uch = userch[uid];
		if (selected[uid] && uch.size() == 100) {
			vector<int> &ids = it->second;
			vector<datetime> &ts = norpntime[uid];
			vector<int> &tie = norpntype[uid];
			user& u = users[uid];
			sort(ids, tie, ts);
			int timeidx = rand() % 6;
			int end = 0;
			while (end < ids.size()) {
				if (hour(t0, ts[end]) > hours[timeidx])
					break;
				end++;
			}
			fprintf(insf, "%d 0 %d %d %d %d %d %d %lf %d\n",uid, u.bi_followers_count , u.followers_count ,u.followee_count,
					u.tweet_count, u.gender, u.verified , dist(mch, uch), hours[timeidx]);
			fprintf(insf, "%d\n", end);
			fprintf(insf, "%d\n", count_circle(uid, ids, end));
			for (int i = 0; i < end; ++i)
				fprintf(insf, "%d ", ids[i]);
			fprintf(insf, "\n");
			for (int i = 0; i < end; ++i)
				fprintf(insf, "%d ", tie[i]);
			fprintf(insf, "\n");
			for (int i = 0; i < end; ++i)
				fprintf(insf, "%d ", hours[timeidx] - hour(t0, ts[i]));
			fprintf(insf, "\n");
		}
		it++;
	}
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
		//		printf("%d\n", n++);
		//		if (n % 1000 == 0)
		//		output();
	}
	fin.close();
	printf("prob done\n");
}



void load_user_profile() {
	printf("load user profile\n");
	vector<string> content[2];
	content[0] = Util::ReadFromFile(user_profile);
	content[1] = Util::ReadFromFile(user_profile2);
	int uid, max_uid;
	int bi_followers_count;
	int city;
	string verified;
	int followers_count;
	string location;
	int province;
	int followee_count;
	string name;
	string gender;
	int tweet_count;
	string created_at;
	string verified_type;
	string description;

	for(int i = 0 ; i < 2 ; i++){


		vector<string>::iterator it = content[i].begin();
		while (it != content[i].end()) {
			string line = it->data();
			//printf("####### line = %s###########\n", line.substr(0,line.size()-1).c_str());
			if (line.at(0) == '#') {
				for (int i = 0; i < 14; i++) {
					it++;
				}
			} else {
				uid = Util::String2Int(line.substr(0,line.size()-1));

				uid = usermap[uid];
				//						printf("line = %s", line.c_str());
				user user(uid);

				it++;
				line = it->data();
				bi_followers_count = Util::String2Int(line.substr(0,line.size()-1));
				if (max_bi_followers_count < bi_followers_count) max_bi_followers_count= bi_followers_count;
				//			printf("line = %s", line.c_str());
				user.setBiFollowerCount(bi_followers_count);


				it++;
				line = it->data();
				city = Util::String2Int(line.substr(0,line.size()-1));
				//			printf("line = %s", line.c_str());
				user.setCity(city);

				it++;
				line = it->data();
				verified = line.substr(0,line.size()-1);
				//			printf("line = %s", line.c_str());
				user.setVerified(verified);

				it++;
				line = it->data();
				followers_count = Util::String2Int(line.substr(0,line.size()-1));
				if(max_followers_count < followers_count)max_followers_count = followers_count;
				//			printf("line = %s", line.c_str());
				user.setFollowerCount(followers_count);

				it++;
				line = it->data();
				location = line.substr(0,line.size()-1);
				//			printf("line = %s", line.c_str());
				user.setLocation(location);

				it++;
				line = it->data();
				province = Util::String2Int(line.substr(0,line.size()-1));
				//			printf("line = %s", line.c_str());
				user.setProvince(province);

				it++;
				line = it->data();
				followee_count = Util::String2Int(line.substr(0,line.size()-1));
				if(max_followee_count < followee_count)max_followee_count = followee_count;
				//			printf("line = %s", line.c_str());
				user.setFolloweeCount(followee_count);

				it++;
				line = it->data();
				name = line.substr(0,line.size()-1);
				//			printf("line = %s", line.c_str());
				user.setName(name);

				it++;
				line = it->data();
				gender = line.substr(0,line.size()-1);
				//			printf("line = %s", line.c_str());
				user.setGender(gender);

				it++;
				line = it->data();
				created_at = line.substr(0,line.size()-1);
				//			printf("line = %s", line.c_str());
				user.setCreatedAt(created_at);

				it++;
				line = it->data();
				verified_type = line.substr(0,line.size()-1);
				//			printf("line = %s", line.c_str());
				user.setVerifiedType(verified_type);

				it++;
				line = it->data();
				tweet_count = Util::String2Int(line.substr(0,line.size()-1));
				if(max_tweet_count <tweet_count) max_tweet_count = tweet_count;
				//			printf("line = %s", line.c_str());
				user.setTweetCount(tweet_count);

				it++;
				line = it->data();
				description = line.substr(0,line.size()-1);
				//			printf("line = %s", line.c_str());
				user.setDescription(description);

				//user.print();
				users[uid] = user;
				it++;
				if(it == content[i].end()) break;
				line = it->data();

			}
			it++;
		}

	}


	//	int num = 0;
	//	for (map<int,user>::iterator uit = users.begin() ; uit != users.end() ;uit++){
	//		uit->second.print();
	//		num++;
	//	}
}




void setDefault() {
	sprintf(network_file, "Z:/weibo/network_snapshot_1/weibo_network.txt");
	sprintf(adoption_file, "Z:/weibo/repost2/source/total.txt");
	sprintf(user_profile, "Z:/weibo/repost2/user_profile1.txt");
	sprintf(user_profile2, "Z:/weibo/repost2/user_profile2.txt");
	sprintf(usermapfile, "D:/Users/zhanpeng/weibo/network2/uidlist.txt");
//	sprintf(network_file, "Z:/weibo/network_snapshot_1/weibo_network_sample.txt");
//	sprintf(adoption_file, "Z:/weibo/repost2/source/total.txt");
//	sprintf(user_profile, "Z:/weibo/repost2/user_profile1.txt");
//	sprintf(user_profile2, "Z:/weibo/repost2/user_profile2.txt");
//	sprintf(usermapfile, "D:/Users/zhanpeng/weibo/network2/uidlist.txt");
	
	delta = 100;

	init_timestamps();
}/*
int loadConfig(int argc, char* argv[]) {
	if (argc < 6)
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
		} else if (strcmp(argv[i], "-u") == 0)  // required
		{
			user_profile = argv[++i];
			++i;
		} else if (strcmp(argv[i], "-u2") == 0)  // required
		{
			user_profile2 = argv[++i];
			++i;
		}else if (strcmp(argv[i], "-m") == 0)  // required
		{
			usermapfile = argv[++i];
			++i;
		}else if (strcmp(argv[i], "-o") == 0)  // required
		{
			char* outputpathchar = argv[++i];
			outputpath = outputpathchar;
			if(outputpath.at(outputpath.length()-1) != '/'){
				outputpath = outputpath + "/";
			}
			//			printf("outputpath = %s\n", outputpath.c_str());
			++i;
		}
		else if (strcmp(argv[i], "-d") == 0)  // required
		{
			delta = atoi(argv[++i]);
			++i;
		}
		else
			++i;
	}
	return 1;
}
 */
void showUsage() {
	printf("Generate features for PSN                               \n");
	printf("                                                             \n");
	printf("Usage: run -g NETWORKFILE -a ADOPTIONFILE -u USERPROFILE -u2 USERPROFILE2 -m USERMAPFILE -o OUTPUTPATH\n");
	printf(" Options:                                                    \n");
	printf(" -d: every d number of reposts, we will output to the disk                                                    \n");
	exit(0);
}

int main(int argc, char* argv[]) {
	srand((unsigned)time(NULL));
	setDefault();
	
	load_selected();
	load_circles();
	load_network();
	load_user_map();
	load_user_profile();
	
	printf("load user map and profile done\n");
	insf = fopen("instances.txt", "w");
	load_ch();
	prob();
	fclose(insf);

	return 0;
}

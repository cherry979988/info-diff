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
#include "analyzer.h"
#include "NetworkData.h"


using namespace std;

// which day in a year(2012) is the beginning of a month ?
const int monthbegin[] = { 0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305,
		335 };

char *network_file;
char *adoption_file;
char *user_profile;
char *user_profile2;
char *usermapfile;
string outputpath;



int max_bi_followers_count = 0;
int max_followers_count = 0;
int max_followee_count = 0;
int max_tweet_count = 0;
int max_post_num = 0;

int delta; //

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
int datespan(datetime &d1, datetime &d2) {
	return monthbegin[d2.month] + d2.day - monthbegin[d1.month] - d1.day;
}

int hourspan(datetime &d1, datetime &d2) {
	return d2.hour - d1.hour;
}

const int N = 1800000;

// the number of users we selected.
int user_num = 0;

user users[N];

map<int, int> usermap;

NetworkData network;


// load the network of the users we selected, 
void load_network() {
	printf("load network\n");
	//	//format: id0 id1 time
	//	FILE *f = fopen(network_file, "r");
	//	int id0, id1, time;
	//	int n = 0;
	//	while (fscanf(f, "%d %d %d\n", &id0, &id1, &time) > 0) {
	//		// load the edges related to the users we selected
	//		// we save one's followers
	//		//if (id0 < user_num || id1 < user_num)
	//		folin[id1].push_back(id0);
	//		n++;
	//		if (n % 10000000 == 0)
	//			printf("%d\n", n);
	//	}
	//	fclose(f);


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
void sort(vector<int> &ids, vector<datetime> &ts) {
	for (int i = 0; i < ids.size(); ++i) {
		for (int j = i + 1; j < ids.size(); ++j) {
			if (ts[j] < ts[i]) {
				int id = ids[i];
				ids[i] = ids[j];
				ids[j] = id;
				datetime t = ts[i];
				ts[i] = ts[j];
				ts[j] = t;
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


void addFeature(int uid, Sample * sample){
	user retweet_user(uid);
	retweet_user = users[uid];

	// add feature for retweet user
	//			printf("mbf  = %d  n = %d, d = %lf  ", max_bi_followers_count, retweet_user.getBiFollowerCount(), (double)retweet_user.getBiFollowerCount()/(double)max_bi_followers_count);
	sample->AddFeature( (double)retweet_user.getBiFollowerCount() /(double)max_bi_followers_count);
	sample->AddFeature( (double)retweet_user.getFollowerCount()/(double)max_followers_count);
	sample->AddFeature( (double)retweet_user.getFolloweeCount()/(double)max_followee_count );
	sample->AddFeature( (double)retweet_user.getTweetCount()/(double)max_tweet_count );
	sample->AddFeature( retweet_user.getGender() );
	sample->AddFeature( retweet_user.getVerified() );

}


int current_post_num = 0;
int output_index = 0;
//statistics in one repost list
//@param rid is the root user id
//@param rmid is the root message id
//@param rp is a repost list
//@param t0 is the time the root blog reposted.

void stat_one(int rid, string rmid, int post_num, map<int, datetime> &rp,
		datetime &t0) {
	printf("=====post i = %d\n", current_post_num++);

	Analyzer analyzer[6];

	if(max_post_num < post_num) max_post_num = post_num;
	map<int, datetime>::iterator iter = rp.begin(), iter1;
	//rpnids saves a user's friends who reposted the root blog before him, the user reposted the blog.
	//norpnids saves all of the user's friends who reposted the root blog, the user didn't repost the blog
	map<int, vector<int> > rpnids, norpnids;
	map<int, vector<datetime> > rpntime, norpntime;
	// record the instances and its own retweet time
	map<int, datetime> rtime;
	map<int, datetime>::iterator rtimeit;

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
					rtime[id2] = t2;
				}
			} else {
				//								printf(" not do!");

				//id2 didn't repost the blogx
				norpnids[id2].push_back(id1);
				norpntime[id2].push_back(t1);
				rtime[id2] = t0; // temporally set the time as root time
			}
			//						printf("\\");
			//}
		}

		//				printf("\n");
		iter++;
	}

	// check the followers of the root
	//	for (int k = 0 ; k < network.edge_to_list[rid].size(); k ++) {
	//		// one of his follower
	//		Edge* edge = network.edge_to_list[rid][k];
	//		// one of root's follower
	//		int fid = edge->v1;
	//		rtimeit = rtime.find(fid);
	//		if (rtimeit == rtime.end()) {
	//			norpnids[fid];
	//			norpntime[fid];
	//			rtime[fid] = t0; // temporally set the time as root time
	//		}
	//	}

	//	printf("===========positive instance============\n");

	// positive instances
	int m = 0;
	map<int, vector<int> >::iterator outit;
	for (outit = rpnids.begin(); outit != rpnids.end(); outit++) {
		//		printf("positive size: %d\n", rpnids.size());

		m++;
		//		printf("m = %d\n", m);

		int uid = outit->first;
		//		printf("uid = %d\n", uid);

		vector<int>& re_followees = outit->second;

		//		printf("followee size = %d\n", re_followees.size());
		vector<datetime>& re_followee_times = rpntime[uid];
		//		printf("followee time size = %d\n", re_followee_times.size());

		datetime t2 = rtime[uid];

		//		printf("c_u:%d c_t:%s r_id:%d, r_mid:%s, r_t:%s", uid, t2.toString().c_str(), rid, rmid.c_str(), t0.toString().c_str());

		int f_index = find_feature_file(t0, t2);

		//		printf("f index = %d\n", f_index);

		//		printf("new positive sample id = %d, m = %d\n", uid, m);

		Sample* sample = new Sample();

		sample->adopted = 1;
		sample->treatednum = re_followees.size();

		//		printf("new feature begin\n");
		addFeature(uid, sample);
		//		printf("add new positive sample to analyzer \n");

		analyzer[f_index].samples.push_back(sample);

		//		printf("add new positive sample to analyzer done! \n");

		//		printf("f index = %d, uid = %s, label = %s, followee size = %s\n",
		//				f_index, features[f_index][0][0].c_str(),
		//				features[f_index][0][3].c_str(),
		//				features[f_index][0][4].c_str());

		//		printf("retweet followee number = %d\n", re_followee_times.size());

		// reset the number of active followees and set the instance into feature files with other timestamp

		for (int i = 0; i < f_index; i++) {
			int followee_size = 0;
			for (int j = 0; j < re_followee_times.size(); j++) {
				datetime re_followee_time = re_followee_times[j];
				int date_diff = datespan(t0, re_followee_time);
				//				printf("date_diff= %d\n", date_diff);
				int hour_diff = hourspan(t0, re_followee_time);
				//				printf("hour_diff= %d\n", hour_diff);
				int time_diff = date_diff * 24 + hour_diff;
				//				printf("time_diff= %d\n", time_diff);
				if (time_diff < timestamps[i]) {
					followee_size++;
				}
			}
			sample = new Sample();
			sample->adopted = 0;
			sample->treatednum = followee_size;
			addFeature(uid, sample);

			analyzer[i].samples.push_back(sample);
			//			printf("f index = %d, uid = %s, label = %s, followee size = %s\n",
			//					f_index, features[i][0][0].c_str(),
			//					features[i][0][3].c_str(), features[i][0][4].c_str());
		}

	}

	//	printf("===========negative instance============\n");

	// negative instances
	for (outit = norpnids.begin(); outit != norpnids.end(); outit++) {

		int uid = outit->first;
		vector<int> re_followees = outit->second;
		vector<datetime>& re_followee_times = norpntime[uid];

		//		printf("c_u:%d c_t:%s\n ", uid);

		Sample* sample = new Sample();
		sample->adopted = 0;
		sample->treatednum = re_followee_times.size();
		addFeature(uid, sample);
		//		printf("add new negative sample to analyzer \n");
		analyzer[5].samples.push_back(sample);
		//		printf("add new negative sample to analyzer done! \n");

		//		printf("retweet followee number = %d\n", re_followee_times.size());

		// reset the number of active followees and set the instance into feature files with other timestamp

		for (int i = 0; i < 5; i++) {
			int followee_size = 0;
			for (int j = 0; j < re_followee_times.size(); j++) {
				datetime re_followee_time = re_followee_times[j];
				int date_diff = datespan(t0, re_followee_time);
				//				printf("date_diff= %d\n", date_diff);
				int hour_diff = hourspan(t0, re_followee_time);
				//				printf("hour_diff= %d\n", hour_diff);
				int time_diff = date_diff * 24 + hour_diff;
				//				printf("time_diff= %d\n", time_diff);
				if (time_diff < timestamps[i]) {
					followee_size++;
				}
			}
			//			printf("followee size at timestamp %d is %d\n", i, followee_size);
			sample = new Sample();
			sample->adopted = 0;
			sample->treatednum = followee_size;
			addFeature(uid, sample);
			analyzer[i].samples.push_back(sample);

		}


	}


	//do propensity score matching
	//	printf("do propensity score matching!\n");

	int idx[] = { 1, 2, 3, 4, 5, 6 };
	char outputfile[200];
	//		printf("path = %s\n", outputpath.c_str());
	for (int i = 0; i < 6; ++i) {
		sprintf(outputfile, "%sinstance-%d.txt", outputpath.c_str(), idx[i]);
		//		printf("file = %s\n", outputfile);
		//		for(int j = 0 ; j < analyzer[i].samples.size();j++){
		//			printf("sample = %s\n", analyzer[i].samples[j]->toString().c_str());
		//		}
		analyzer[i].Analysis(1, outputfile);
	}

	for (int i = 0; i < 6; ++i) {
		analyzer[i].deleteSamples();
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
	network_file =
			"/Users/zhangjing0544/Dropbox/workspace4c/Retweet/src/network_sample.txt";
	adoption_file =
			"/Users/zhangjing0544/Dropbox/workspace4c/Retweet/src/adoptions.txt";
	user_profile =
			"/Users/zhangjing0544/Dropbox/workspace4c/Retweet/src/user_profile.txt";
	usermapfile = "/Users/zhangjing0544/Dropbox/workspace4c/Retweet/src/usermapfile.txt";
	//outputpath = "/Users/zhangjing0544/Dropbox/workspace4c/Retweet/";
	delta = 100;

	init_timestamps();
}
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

void showUsage() {
	printf("Generate features for PSN                               \n");
	printf("                                                             \n");
	printf("Usage: run -g NETWORKFILE -a ADOPTIONFILE -u USERPROFILE -u2 USERPROFILE2 -m USERMAPFILE -o OUTPUTPATH\n");
	printf(" Options:                                                    \n");
	printf(" -d: every d number of reposts, we will output to the disk                                                    \n");
	exit(0);
}


// Use propensity score matching to test whether the retweet behaviors from the followees can boost the retweet probability.

int main(int argc, char* argv[]) {
	setDefault();
	printf("set default value for parameters done\n");
	if (!loadConfig(argc, argv)) {
		showUsage();
		exit(0);
	}
	printf("load configuration done\n");
	load_network();
	//printNetwork();
	load_user_map();
	load_user_profile();
	printf("load user map and profile done\n");
	prob();



	return 0;
}

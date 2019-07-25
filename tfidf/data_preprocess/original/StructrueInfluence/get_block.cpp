
// to find out all the circles of a user's followees and save it to a file.
// this work is to simplify the subsequent works which will use the circles of a user's followees.

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
#include <list>
using namespace std;

// there is almost 1,800,000 users in the original network, but we just sample 300,000 of them.
// selected[i] == 1 means the i's user is selected.
// folout[i] saves the followees of the i's user.
const int N = 1800000;
int selected[N];
set<int> folout[N];

// we use deep-first search to find out the circle of a user's followees.
// markn1 , neign1, markn2, neign2 is temporary variables while doing the deep-first wearch.
// We specify circle as k-brace circle, which is defined as the circle with all the edges of embeddedness less
// than k being removed, where embeddedness of an edge is the number of common friends shared by the two endpoints.
// a variable with a suffix n1 is used for 1-brace circle and n2 for 2-brace circle.
int markn1[500000];
list<int> neign1[500000];
int markn2[500000];
list<int> neign2[500000];
int follows[500000];

// these are the output file.
FILE *blockn1 = NULL;
FILE *blockn2 = NULL;
char* network_file;

// load the selected users and store them in the array 'selected'.
void load_users() {
	memset(selected, 0, N * 4);
	FILE *userf = fopen("D:/Users/liubiao/repost2/source/users_idx.txt", "r");
	int id;
	while (fscanf(userf, "%d", &id) > 0)
		selected[id] = 1;
	fclose(userf);
}

// deep-first search (1-brace)
// idx is the index of the current node
// block_num is the index of the block that the node blongs to. 
void dfsn1(int idx, int block_num) {
	if (markn1[idx] == 0) {
		markn1[idx] = 1;
		// save the node and the block id to a file
		fprintf(blockn1, "%d %d ", follows[idx], block_num);
		list<int>::iterator it = neign1[idx].begin();
		while (it != neign1[idx].end()) {
			if (markn1[*it] == 0)
				dfsn1(*it, block_num);
			++it;
		}
	}
}

// deep-first search (2-brace)
void dfsn2(int idx, int block_num) {
	if (markn2[idx] == 0) {
		markn2[idx] = 1;
		fprintf(blockn2, "%d %d ", follows[idx], block_num);
		list<int>::iterator it = neign2[idx].begin();
		while (it != neign2[idx].end()) {
			if (markn2[*it] == 0)
				dfsn2(*it, block_num);
			++it;
		}
	}
}

// count the number of common friends of id1 and id2. 
int check(int id1, int id2) {
	set<int> &out1 = folout[id1];
	set<int> &out2 = folout[id2];
	if (out1.find(id2) == out1.end())
		return 0;
	if (out2.find(id1) == out2.end())
		return 0;
	int n = 0;
	set<int>::iterator it = out1.begin();
	while (it != out1.end()) {
		int id3 = *it;
		set<int> &out3 = folout[id3];
		if (out3.find(id1) != out3.end() && out3.find(id2) != out3.end() && out2.find(id3) != out2.end())
			n++;
		if (n > 2)
			break;
		it++;
	}
	return n;
}

// find out the circles of id's followees.
void get_block(int id) {
	set<int>& out = folout[id];
	int size = out.size();
	int i = 0;

	// construct the graph of id's followees.
	// we save the user's ids to an array named 'follows' and 
	// we will use the index of the array instead of the user's id while doing deep-first search .
	for (set<int>::iterator it = out.begin(); it != out.end(); ++it) {
		markn1[i] = markn2[i] = 0;
		neign1[i].clear();
		neign2[i].clear();
		follows[i] = *it;
		++i;
	}
	for (int i = 0; i < size; ++i) {
		int id1 = follows[i];
		for (int j = i + 1; j < size; ++j) {
			int id2 = follows[j];
			int com = check(id1, id2);
			if (com == 1) {
				neign1[i].push_back(j);
				neign1[j].push_back(i);
			} else if (com > 1) {
				neign1[i].push_back(j);
				neign1[j].push_back(i);
				neign2[i].push_back(j);
				neign2[j].push_back(i);
			}
		}
	}

	// find out the circles using deep-first search. 
	fprintf(blockn1, "%d ", id);
	fprintf(blockn2, "%d ", id);
	int block_num = 0;
	for (int i = 0; i < size; ++i) {
		if (markn1[i] == 0) {
			dfsn1(i, block_num);
			block_num++;
		}
	}
	block_num = 0;
	for (int i = 0; i < size; ++i) {
		if (markn2[i] == 0) {
			dfsn2(i, block_num);
			block_num++;
		}
	}
	fprintf(blockn1, "\n");
	fprintf(blockn2, "\n");
}

// load a user's followees and find out the circles among them.
void load_network() {
	cout << "load network" << endl;
	FILE *f = fopen(network_file, "r");
	int id0, id1, time, n = 0;
	while (fscanf(f, "%d %d %d\n", &id0, &id1, &time) > 0) {
		folout[id0].insert(id1);
		n++;
		if (n % 1000000 == 0)
			printf("%d\n", n);
	}
	fclose(f);
	cout << "network done" << endl;
	cout << "get blcoks" << endl;
	blockn1 = fopen("blocksn1.txt", "w");
	blockn2 = fopen("blocksn2.txt", "w");
	for (int i = 0; i < N; ++i) {
		if (i % 1000 == 0)
			cout << i << endl;
		if (folout[i].size() == 0)
			continue;
		//if (selected[i])
		get_block(i);
	}
	fclose(blockn1);
	fclose(blockn2);
	cout << "blocks done!" << endl;

}
void setDefault() {
	network_file =
			"/Users/zhangjing0544/Dropbox/workspace4c/Retweet/src/network_sample.txt";
}
int loadConfig(int argc, char* argv[]) {
	if (argc < 1)
		return 0;
	int i = 1;
	while (i < argc) {
		if (strcmp(argv[i], "-g") == 0)  // required
		{
			network_file = argv[++i];
			++i;
		}
		else
			++i;
	}
	return 1;
}

void showUsage() {
	printf("Generate circles for each user                               \n");
	printf("                                                             \n");
	printf("Usage: run -g NETWORKFILE \n");
	printf(" Options:                                                    \n");
	exit(0);
}
int main(int argc, char* argv[]) {
	setDefault();
	printf("set default value for parameters done\n");
	if (!loadConfig(argc, argv)) {
		showUsage();
		exit(0);
	}
	printf("load configuration done\n");
	//load_users();
	load_network();
	return 0;
}

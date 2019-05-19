#pragma once

#include <iostream>
#include <vector>

using namespace std;

struct Edge{
public:
	int v1, v2;  //From v1 to v2	
	char type;
	double sim;
};


class NetworkData
{
public:
	NetworkData(void);
	~NetworkData(void);

	int nodenum, edgenum, typenum;
	vector<Edge*>* edge_from_list;
	vector<Edge*>* edge_to_list;
	
	void ReadNetwork(const char* filename);


private:
	Edge* edges;
};



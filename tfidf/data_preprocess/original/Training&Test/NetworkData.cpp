#include "NetworkData.h"
#include <stdio.h>


NetworkData::NetworkData(void)
{
	typenum = 2;
}


NetworkData::~NetworkData(void)
{
	delete[] edges;
}


void NetworkData::ReadNetwork(const char* filename) {
	printf("Reading network from \"%s\"...\n", filename);
	FILE *f = fopen(filename, "r");
	fscanf(f, "%d%d\n", &(this->nodenum), &(this->edgenum));
//	printf(" node number = %d, edge number = %d\n", this->nodenum, this->edgenum);
	//edge_from_list = new vector<Edge*>[nodenum];
	edge_to_list = new vector<Edge*>[nodenum];
	edges = new Edge[edgenum];
	int v1id, v2id, fnum, type, eid = 0;
	for (int i = 0; i < nodenum; ++i) {
		fscanf(f, "%d", &v1id);
		fscanf(f, "%d", &fnum);
//		printf("current node = %d, edge number = %d\n", v1id, fnum);
		for (int j = 0; j < fnum; ++j) {
			fscanf(f, "%d%d", &v2id, &type);
//			printf(" target node = %d, type = %d\n", v2id, type);
			Edge* e = edges + eid;
			e->v1 = v1id;
			e->v2 = v2id;
			e->type = type;
			//edge_from_list[v1id].push_back(e);
			edge_to_list[v2id].push_back(e);
			++eid;
		}
		if (i == nodenum - 1 || i % 10000 == 0) printf("\r%.1lf percents completed...", (double)(i+1)/nodenum*100);
	}
	printf("\n");
	fclose(f);
}



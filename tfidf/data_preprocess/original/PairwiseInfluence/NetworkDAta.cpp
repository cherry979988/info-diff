#include "NetworkData.h"

NetworkData::NetworkData(void) {
	typenum = 2;
}

NetworkData::~NetworkData(void) {
	delete[] edges;
}

void NetworkData::ReadNetwork(const char* filename) {
	printf("Reading network from \"%s\"...\n", filename);
	FILE *f = fopen(filename, "r");
	fscanf(f, "%d%d\n", &(this->nodenum), &(this->edgenum));
	printf(" node number = %d, edge number = %d\n", this->nodenum,
			this->edgenum);
	//edge_from_list = new vector<Edge*>[nodenum];
	edge_to_list = new vector<Edge*> [nodenum];
	edges = new Edge[edgenum];
	int v1id, v2id, fnum, type, eid = 0;
	double sim;
	//nodenum = 185214; /////hare code node number for small dataset
	for (int i = 0; i < nodenum; ++i) {
		fscanf(f, "%d", &v1id);
		fscanf(f, "%d", &fnum);
//		printf("=====current node = %d, edge number = %d=======\n", v1id, fnum);
		double max_sim = 0;
		for (int j = 0; j < fnum; ++j) {
			fscanf(f, "%d%d", &v2id, &type);
			Edge* e = edges + eid;
			e->v1 = v1id;
			e->v2 = v2id;
			e->type = type;
			//e->sim = sim;
			//printf("sim = %lf, max_sim = %lf\n", sim, max_sim);
//			if (sim > max_sim) {
//				max_sim = sim;
//			}
			//edge_from_list[v1id].push_back(e);
			edge_to_list[v2id].push_back(e);
			++eid;
		}

		// normalize the similarity value

//		for (int j = 0; j < fnum; ++j) {
//
//			Edge* edge = edge_from_list[v1id][j];
////			printf("origianl sim = %lf\n", edge->sim);
//			edge->sim = edge->sim / max_sim;
////			printf("----target node = %d, type = %d, max_sim = %lf, sim = %lf\n",
////					edge->v2, type, max_sim, edge->sim);
//
//		}

		if (i == nodenum - 1 || i % 10000 == 0)
			printf("\r%.1lf percents completed...",
					(double) (i + 1) / nodenum * 100);
	}
	printf("\n");
	fclose(f);
}


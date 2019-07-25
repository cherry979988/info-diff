#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <algorithm>
#include <cstring>
#include <vector>
#include <set>
#include <map>
#include <time.h>

using namespace std;

int selected[1800000];
set<int> network[1800000];

void load_selected() {
	printf("load selected\n");
	FILE *sel = fopen("Z:/weibo/repost2/source/c++/instance/instance/users.txt", "r");
	int uid;
	while (fscanf(sel, "%d", &uid) > 0)
		selected[uid] = 1;
	fclose(sel);
	printf("selected done\n");
}

class relation
{
public:
    int user_id;
    int target_id;
};

vector<relation> rel;
int rel_cnt = 0;
int max_user_id;
int * first;

bool cmp(const relation &v0, const relation &v1) {
	return v0.user_id < v1.user_id;
}

int main(int argc, char ** argv)
{

	srand(time(NULL));
    FILE * fin = fopen(argv[1], "r");
    FILE * fout = fopen(argv[2], "w");
    
    int u, v;
    fscanf(fin, "%d %d", &u, &v);
    while (u--) {
        int id, m;
        fscanf(fin, "%d %d", &id, &m);
        if (id > max_user_id)
            max_user_id = id;
        
        while (m--) {
            int tar, type;
            fscanf(fin, "%d %d", &tar, &type);
			if (selected[id])
				network[id].insert(tar);
            if (type == 1) {
                relation tmp;
                tmp.user_id = id;
                tmp.target_id = tar;
                rel.push_back(tmp);
                rel_cnt++;
            }

            relation tmp;
            tmp.user_id = id;
            tmp.target_id = tar;
            rel.push_back(tmp);

            rel_cnt++;
        }
    }
    cout << "Load Done" << endl;
    
    sort(rel.begin(), rel.begin() + rel_cnt, cmp);
    
    first = new int[max_user_id + 2];
	memset(first, 0xff, sizeof(int) * (max_user_id + 2));
	for (int i = rel_cnt - 1; i >= 0; i--)
		first[rel[i].user_id] = i;
	first[max_user_id + 1] = rel_cnt;
	for (int i = max_user_id; i >= 0; i--)
		if (first[i] < 0)
			first[i] = first[i + 1];
    fclose(fin);
    
    cout << "Build Done" << endl;
    
    int * res = new int[max_user_id + 2];
    int * flag = new int[max_user_id + 2];
	memset(res, 0xff, sizeof(int) * (max_user_id + 2));
	memset(flag, 0xff, sizeof(int) * (max_user_id + 2));
    
    fin = fopen(argv[1], "r");
    
    fscanf(fin, "%d %d", &u, &v);
    fprintf(fout, "%d %d\n", u, v);
    int tot = 0;
    while (u--) {
        if (tot && (tot % 10000 == 0))
            cout << tot << endl;
        tot++;
        int id, m;
        fscanf(fin, "%d %d", &id, &m);
		if (!selected[id]) {
			while (m--) {
				int tar, type;
				fscanf(fin, "%d %d", &tar, &type);
			}
			continue;
		}
        fprintf(fout, "%d %d", id, m);
        int step = atoi(argv[3]);
        int re_rate = (double) atoi(argv[4]) / 100;
        int usr = id;
        flag[id] = id;
        res[id] = 0;
		while (step--) {
            
            int c = first[usr + 1] - first[usr];
            if (c == 0) {
                usr = id;
                continue;
            }
            
            int k = rand() % 100;
			if (k >= re_rate) {
				int id1 = 0;
				while (1) {
					long long r = (long long)rand() * rand() % c;
					id1 = rel[first[usr] + r].target_id;
					if (network[id].find(id1) != network[id].end())
						break;
				}
				usr = id1;
			} else {
				usr = id;
				step++;
			}
            if (flag[usr] != id) {
                res[usr] = 0;
            }
            flag[usr] = id;
            res[usr]++;
        }
        while (m--) {
            int tar, type;
            fscanf(fin, "%d %d", &tar, &type);
            fprintf(fout, " %d %d %lf", tar, type, (double) res[tar] / atoi(argv[3]));
        }
        fprintf(fout, "\n");
    }

    fclose(fin);
    fclose(fout);
    return 0;
}


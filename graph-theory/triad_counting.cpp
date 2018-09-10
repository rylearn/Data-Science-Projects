#include "stdafx.h"
#include "Snap.h"
#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <algorithm>
#include <climits>
#include <math.h>
#include <ctime>
#include <stdlib.h>
#include <utility>
#include <iterator>
#include <tuple>
using namespace std;


int main(int argc, char* argv[]) {

	const TStr graph_filename = TStr("epinions-signed.txt");
	PUNGraph g = TSnap::LoadEdgeList<PUNGraph>(graph_filename, 0, 1);

	string line;
	ifstream myfile("epinions-signed.txt");
	int i = 0;
	map<pair<int, int>, int> signs;
	if (myfile.is_open())
	{
		while (getline(myfile, line))
		{
			int a, b, c;
			if (i < 2) {
				cout << line << '\n';
				i += 1;
			}
			stringstream ss(line);
			ss >> a >> b >> c;
			auto temp = make_pair(a, b);
			auto temp2 = make_pair(b, a);
			signs[temp] = c;
			signs[temp2] = c;

		}
		myfile.close();
	}

	cout << g->GetEdges() << endl;
	TSnap::DelSelfEdges(g);
	cout << g->GetEdges() << endl;

	map<tuple<int, int, int>, bool> triad_dict;
	vector<int> triad_counts(5);

	for (TUNGraph::TNodeI NI = g->BegNI(); NI < g->EndNI(); NI++) {
		int curr_id = NI.GetId();
		int num_neigh = NI.GetOutDeg();
		for (int j = 0; j < num_neigh; ++j) {
			int neigh_id = NI.GetNbrNId(j);
			TIntV newVal;
			int num_triads = TSnap::GetCmnNbrs(g, curr_id, neigh_id, newVal);

			for (int r = 0; r < num_triads; ++r) {
				int someNodeId = newVal[r];
				int smallest; int medium; int large;
				vector<int> elemsIds; 
				elemsIds.push_back(curr_id);
				elemsIds.push_back(neigh_id);
				elemsIds.push_back(someNodeId);
				sort(elemsIds.begin(), elemsIds.end());
				smallest = elemsIds[0]; medium = elemsIds[1]; large = elemsIds[2];
				tuple<int, int, int> newTup = make_tuple(smallest, medium, large);
				if (triad_dict.find(newTup) == triad_dict.end()) {
					triad_dict[newTup] = true;
					// not found
					auto sign1 = signs[make_pair(curr_id, neigh_id)];
					auto sign2 = signs[make_pair(curr_id, someNodeId)];
					auto sign3 = signs[make_pair(someNodeId, neigh_id)];

					bool match1 = false;
					bool match2 = false;
					bool match3 = false;

					if (sign1 == sign2) {
						match1 = true;
					}
					if (sign2 == sign3) {
						match2 = true;
					}
					if (sign1 == sign3) {
						match3 = true;
					}

					if (match1 && match2 && match3)
						if (sign1 < 0)
							triad_counts[0] += 1;
						else
							triad_counts[3] += 1;
					else if (match1 == match2)
						if (sign1 < 0)
							triad_counts[1] += 1;
						else
							triad_counts[2] += 1;
					else if (match2 == match3)
						if (sign2 < 0)
							triad_counts[1] += 1;
						else
							triad_counts[2] += 1;
					else if (match1 == match3)
						if (sign1 < 0)
							triad_counts[1] += 1;
						else
							triad_counts[2] += 1;
				}
			}
		}
	}
	for (int q = 0; q < 5; ++q) {
		cout << triad_counts[q] << endl;
	}
	

	return 0;
}


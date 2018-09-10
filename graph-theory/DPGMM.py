import math
import pickle

import itertools

import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt

from sklearn import mixture
import networkx as nx
import snap

np.random.seed(0)
limits=plt.axis('off')

def gather_graphs(graph_ids):
    ids = []
    Gs = []
    for i in graph_ids:
        filename = './jermain_gexf_files/%d.gexf'%i
        try:
            NetworkXGraph = nx.readwrite.gexf.read_gexf(filename)
            nx.write_edgelist(NetworkXGraph, 'temp.edges')
            G = snap.LoadEdgeList(snap.PUNGraph, 'temp.edges', 0, 1)
            Gs.append(G)
            ids.append(i)
        except:
            continue
    return ids, Gs

def cosine_similarity(G, e):
    shared_neighbors = 0
    n1 = G.GetNI(e.GetSrcNId())
    n2 = G.GetNI(e.GetDstNId())

    for i in range(n1.GetDeg()):
        neighborId = n1.GetNbrNId(i)
        if G.IsEdge(neighborId, n2.GetId()): shared_neighbors += 1
    shared_neighbors += 2 # include n1 and n2

    return shared_neighbors / math.sqrt((1+n1.GetDeg())*(1+n2.GetDeg()))


def cosine_similarities(G):
    result = {}
    for e in G.Edges():
      result[(e.GetSrcNId(), e.GetDstNId())] = cosine_similarity(G, e)
    return result

# Used only for simulating data for verification
def sine_distribution(x, n):
    return .5*math.cos(x*math.pi*(2*n-2)) + .5


def test_grouping(clusters=4):
    n_samples = 1000
    X = np.zeros((n_samples, 1))
    i = 0
    while i < n_samples:
        x = (np.random.random(), np.random.random())
        if x[1] < sine(x[0], clusters):
            X[i] = x[0]
            i += 1
    return X

def film_samples(write=False):
    [ids, graphs] = gather_graphs(range(1, 1000))
    tie_strengths = {}

    for i, Gid in enumerate(ids):
        strengths = cosine_similarities(graphs[i])
        if write:
            with open('./tie_strengths/%d.tie_strengths.txt'%Gid, 'wt') as f:
                for edge in strengths:
                    f.write('%d, %d, %f\n'%(edge[0], edge[1], strengths[edge]))

        tie_strengths.update(strengths)

    X = np.ndarray((len(tie_strengths),1), 
            buffer=np.array(tie_strengths.values()))
    return X

def read_X(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    lines = map(float, lines) 
    X = np.ndarray((len(lines), 1), buffer=np.array(lines))
    return X
		
def write_X(X, filename):
    X = X.reshape(-1,)
    with open(filename,'wt') as f:
        f.writelines('\n'.join(map(str,X)))
    return

def histogram(X):
    num_bins = 20
    n, bins, patches = plt.hist(X, num_bins, facecolor='blue', alpha=0.5, 
            edgecolor='black', linewidth=1.2)
    plt.title('Tie Strengths Across All Films')
    plt.xlabel('Tie Strength')
    plt.ylabel('Rel Frequency')
    plt.axvline(x=.59731372, color='orange', label = 'C_1: 0.597')
    plt.axvline(x=.99994855, color='orange', label = 'C_2: 0.999')
    plt.legend()
    plt.show()

def illustrate(Gid):
    filename = './jermain_gexf_files/%d.gexf'%Gid
    nxG = nx.readwrite.gexf.read_gexf(filename)
    nx.write_edgelist(nxG, 'temp.edges')
    G = snap.LoadEdgeList(snap.PUNGraph, 'temp.edges', 0, 1)
    tie_strengths = cosine_similarities(G)
    edge_colors = []
    for u, v in nx.edges(nxG):
        u = int(u)
        v = int(v)
        if (u, v) in tie_strengths.keys():
            if tie_strengths[(u, v)] > .98: edge_colors.append('r') 
            else: edge_colors.append('b')
        elif (v, u) in tie_strengths.keys():
            if tie_strengths[(v, u)] > .98: edge_colors.append('r') 
            else: edge_colors.append('b')
    nx.draw_networkx(nxG, node_size=5, with_labels=False,
            edge_color=edge_colors)
    plt.show()

def main():
    illustrate(316)
    return
    C = 2
    X = read_X('tie_strengths.csv')
    histogram(X)
		
    dpgmm = mixture.BayesianGaussianMixture(
            n_components=C, covariance_type='full',
            max_iter=500,
            weight_concentration_prior_type='dirichlet_process').fit(X)

    print dpgmm.means_
    Y = dpgmm.predict(X)
    for i in range(C):
        print 'C %d: %d'%(i,sum([y == i for y in Y]))

if __name__ == '__main__':
    main()

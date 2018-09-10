import networkx as nx
import snap
import os
import numpy as np

def gexfToSnap(gexfID):
    try: 
        gexfFile = 'jermain_gexf_files/%d.gexf' % gexfID
        edgesFile = '%d.edges' % gexfID
        networkXGraph = nx.readwrite.gexf.read_gexf(gexfFile)
        nx.write_edgelist(networkXGraph, edgesFile)
        snapGraph = snap.LoadEdgeList(snap.PUNGraph, edgesFile, 0, 1)
        os.remove(edgesFile)
        return snapGraph
    except IOError:
        return None

def getCharacteristicPathLength(graph):
    averagePathLengthSum = 0
    for node in graph.Nodes():
        averagePathLengthSum += snap.GetFarnessCentr(graph, node.GetId())
    return float(averagePathLengthSum) / graph.GetNodes()

def getTransitivity(graph):
    # This coefficient is kind of unimportant but we should probably decide on what it should be. Some sources say 2, others 3
    triangleCoefficient = 2
    triadSum = 0.0
    degreeSum = 0.0
    for node in graph.Nodes():
        triadSum += snap.GetNodeTriads(graph, node.GetId())
        nodeDeg = node.GetDeg()
        degreeSum += nodeDeg * (nodeDeg - 1)
    return triangleCoefficient * triadSum / degreeSum

def getTieStrengths(gexfID):
    strengths = []
    with open('tie_strengths/%d.tie_strengths.txt' % gexfID, 'r') as file:
        for line in file:
            node1, node2, strength = line.split(', ')
            strengths.append(float(strength))
    return strengths

def getMaxBetweennessCentrality(graph):
    nodeTable = snap.TIntFltH()
    edgeTable = snap.TIntPrFltH()
    snap.GetBetweennessCentr(graph, nodeTable, edgeTable, 1.0)
    betweennessCentralities = [nodeTable[node] for node in nodeTable]
    numNodes = graph.GetNodes()
    # Normalize by the max betweenness centrality that a node in this graph could have
    return 2 * np.max(betweennessCentralities) / ((numNodes - 1) * (numNodes - 2))

def main():
    vecList = []
    for i in range(1000):
        snapGraph = gexfToSnap(i)
        if snapGraph:
            featureVec = []
            featureVec.append(i)
            featureVec.append(snap.GetClustCf(snapGraph, -1))
            featureVec.append(getTransitivity(snapGraph))
            featureVec.append(getCharacteristicPathLength(snapGraph))
            tieStrengths = getTieStrengths(i)
            featureVec.append(np.mean(tieStrengths))
            featureVec.append(np.std(tieStrengths))
            featureVec.append(getMaxBetweennessCentrality(snapGraph))
            vecList.append(featureVec)
    np.savetxt('featureMatrix.csv', np.matrix(vecList), fmt=['%d', '%f', '%f', '%f', '%f', '%f', '%f'])

if __name__ == "__main__":
    main()
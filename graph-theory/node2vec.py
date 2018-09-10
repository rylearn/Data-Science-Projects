
import networkx as nx
import snap
import pickle
import matplotlib.pyplot as plt
import numpy as np
import node2vec
from gensim.models import Word2Vec
from sklearn.cluster import KMeans

def load_dictionary(file_name):
    with open(file_name + '.pkl', 'rb') as current_file:
        return pickle.load(current_file)

def update_keys(dictTags):
    dict_movie_name_to_tags = {}
    for test_url, list_tags in dictTags.iteritems():
        exploded_string = test_url.split('/')
        exploded_again_string = exploded_string[-1].split('-')
        movie_list = exploded_again_string[1:]
        movie_title = ' '.join(movie_list)
        dict_movie_name_to_tags[movie_title] = dictTags[test_url]
    return dict_movie_name_to_tags

def extractGraph(filename):
    NetworkXGraph = nx.readwrite.gexf.read_gexf(filename)
    newFileName = filename.split('.')
    finalFileName = newFileName[0] + '.edges'
    nx.write_edgelist(NetworkXGraph, finalFileName)
    SNAPGraph = snap.LoadEdgeList(snap.PUNGraph, finalFileName, 0, 1)
    return SNAPGraph

def drawBasicGraph(nx_graph):
    nx.draw(nx_graph)
    plt.draw()
    plt.show()

def doNode2VecStuff(nx_graph, filename = 'sample.txt', p = 1, q = 2, num_walks = 10, walk_length = 80,
                   dimensions = 2, window_size = 10, num_workers = 10, num_iters = 5):
    Graph_n2v = node2vec.Graph(nx_graph, False, p, q) # p and q param
    Graph_n2v.preprocess_transition_probs()
    walks = Graph_n2v.simulate_walks(num_walks, walk_length)
    walks = [map(str, walk) for walk in walks]
    
    model = Word2Vec(walks, size=dimensions, window=window_size, min_count=0, sg=1, workers=num_workers, iter=num_iters)
    
    model.wv.save_word2vec_format(filename, binary = False)

def processWord2Vec(filename='sample.txt'):
    with open(filename) as f:
        content = f.readlines()

    complete_list_values = []
    tuple_id_to_vector = []
    for ind in range(len(content)):
        if ind == 0:
            continue
        values_list = []
        exploded_list = content[ind].split(' ')
        for i in range(len(exploded_list)):
            if i == 0:
                key = int(exploded_list[i])
            else:
                values_list.append(float(exploded_list[i]))
        complete_list_values.append(values_list)
        tuple_id_to_vector.append((key, values_list))
    np_array = np.asarray(complete_list_values)
    return np_array, tuple_id_to_vector

def doKMeans(np_array, num_clusters=5):
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(np_array)

    labels = kmeans.predict(np_array)
    centroids = kmeans.cluster_centers_
    return labels

# returns: list of 5 lists associated with 5 clusters
# each list contains node ids
def getNodeIdsClusters(labels, tuple_id_to_vector, num_clusters = 5):
    degs = [] # keeps track of degrees associated with each cluster
    node_ids_groups = []
    for i in range(num_clusters):
        degs.append([])
        node_ids_groups.append([])
    for i in range(len(labels)):
        node_id = tuple_id_to_vector[i][0]
        node = snapGraph.GetNI(node_id)
        node_degree = node.GetDeg()
        degs[labels[i]].append(node_degree)
        node_ids_groups[labels[i]].append(node_id)
    return node_ids_groups

def determineBridgeNodes(node_ids_groups):
    list_bridge_node_ids = []
    for i in range(len(node_ids_groups)):
        # for each node id group, 
        # determine which node id
        # corresponds to highest edges
        # to nodes not in group
        current_group = node_ids_groups[i]
        outgoing_edge_counts = []
        for j in range(len(current_group)):
            current_node = snapGraph.GetNI(current_group[j])

            current_degree = current_node.GetDeg()
            num_edges_outside = 0
            for k in range(current_degree):
                neighbor_id = current_node.GetNbrNId(k)

                if neighbor_id not in current_group: # the key line
                    num_edges_outside += 1

            outgoing_edge_counts.append(num_edges_outside)
        max_elem = max(outgoing_edge_counts)
        curr_max_index = outgoing_edge_counts.index(max_elem)
        max_node_id = current_group[curr_max_index]

        # not needed, but for reference
        max_node = snapGraph.GetNI(max_node_id)
        max_degree = max_node.GetDeg()

        list_bridge_node_ids.append(max_node_id)
    return list_bridge_node_ids


# main
# not necessary to process all movies now
dictTags = load_dictionary('tags')  #
dict_movie_name_to_tags = update_keys(dictTags) #

# do node2vec
new_graph_filename = "gexf_files/660.gexf" # Pulp fiction
snapGraph = extractGraph(new_graph_filename)
nx_graph = nx.readwrite.gexf.read_gexf(new_graph_filename)
doNode2VecStuff(nx_graph)
np_array, tuple_id_to_vector = processWord2Vec()

# do kmeans
labels = doKMeans(np_array)
node_ids_groups = getNodeIdsClusters(labels, tuple_id_to_vector)
list_bridge_node_ids = determineBridgeNodes(node_ids_groups) # figure out bridge nodes
print list_bridge_node_ids

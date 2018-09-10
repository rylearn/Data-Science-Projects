
import networkx as nx
import snap
import csv
import time
import numpy as np
import torch
import pandas as pd
import pickle

from sklearn.metrics import roc_curve, auc
from sklearn import metrics
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MultiLabelBinarizer


def extractSnapGraph(filename):
    NetworkXGraph = nx.readwrite.gexf.read_gexf(filename)
    newFileName = filename.split('.')
    finalFileName = newFileName[0] + '.edges'
    print finalFileName
    nx.write_edgelist(NetworkXGraph, finalFileName)
    SNAPGraph = snap.LoadEdgeList(snap.PUNGraph, finalFileName, 0, 1)
    return SNAPGraph

def extractNetworkXGraph(filename):
    NetworkXGraph = nx.readwrite.gexf.read_gexf(filename)
    return NetworkXGraph

def load_dictionary(file_name):
    with open(file_name + '.pkl', 'rb') as current_file:
        return pickle.load(current_file)

## initially get dictionaries and modify them to map genres to numbers
dictGenresToIds = load_dictionary('genre_to_ids')
dictIdToGenres = load_dictionary('id_to_genres')
dictIdToMovieName = load_dictionary('id_to_movie_name')

genres = []
for key, value in dictGenresToIds.iteritems():
    genres.append(key)

genres_to_ids = {}
for i in range(len(genres)):
    genres_to_ids[genres[i]] = i

new_dictIdToGenres = {}
for movie_id, genres_list in dictIdToGenres.iteritems():
    if movie_id not in new_dictIdToGenres.iterkeys():
        new_dictIdToGenres[movie_id] = []
    for i in range(len(genres_list)):
        genre = genres_list[i]
        new_dictIdToGenres[movie_id].append(genres_to_ids[genre])

new_dictIdToBinaryGenres = {} # id maps to a bit vector
for movie_id, genres_ids_list in new_dictIdToGenres.iteritems():
    bit_vector = []
    
    for i in range(len(genres)):
        if i in genres_ids_list:
            bit_vector.append(1)
        else:
            bit_vector.append(0)
    new_dictIdToBinaryGenres[movie_id] = bit_vector

new_dictGenresToIds = {}
for genre, ids_list in dictGenresToIds.iteritems():
    genre_id = genres_to_ids[genre]
    new_dictGenresToIds[genre_id] = ids_list

# pre-processing done
# prediction starts here
new_df = pd.read_csv('featureMatrix.csv', sep=' ')

X_data = []
Y_data = []
for index, row in new_df.iterrows():
    movie_id = row[0]
    if movie_id in new_dictIdToBinaryGenres.iterkeys():
        genres_list = new_dictIdToBinaryGenres[movie_id]
        Y_data.append(genres_list)
    else:
        continue
    new_movie = []
    for i in range(1, len(row)):
        new_movie.append(row[i])
    X_data.append(new_movie)

X_data = np.asarray(X_data)
Y_data = np.asarray(Y_data)

X_train = X_data[0:700]
Y_train = Y_data[0:700]

X_test = X_data[700:-1]
Y_test = Y_data[700:-1]

mlp = MLPClassifier(activation='tanh', solver='adam', alpha=1e-2, batch_size = 10,
                    learning_rate = 'invscaling', tol = 0.000001,
                    hidden_layer_sizes=(100, 2), max_iter = 1000, random_state=1)

mlp.fit(X_train, Y_train)

score = mlp.score(X_test, Y_test) # num of rows that matches exactly, very low

Y_mlp_result = mlp.predict(X_test)

true_positive = 0
true_negative = 0
false_positive = 0
false_negative = 0
count = 0
for i in range(len(Y_mlp_result)):
    for j in range(len(Y_mlp_result[i])):
        count += 1
        if Y_test[i][j] == 1 and Y_mlp_result[i][j] == 1:
            true_positive += 1
        if Y_test[i][j] == 0 and Y_mlp_result[i][j] == 0:
            true_negative += 1
        if Y_test[i][j] == 1 and Y_mlp_result[i][j] == 0:
            false_negative += 1
        if Y_test[i][j] == 0 and Y_mlp_result[i][j] == 1:
            false_positive += 1


right = true_negative + true_positive
total = true_positive + true_negative + false_positive + false_negative

print float(right)/total

fpr = float(false_positive) / (false_positive + true_negative)
tpr = float(true_positive) / (true_positive + false_negative)

y = np.array([1, 1, 2, 2])
pred = np.array([0.1, 0.4, 0.35, 0.8])
fpr, tpr, thresholds = metrics.roc_curve(y, pred, pos_label=2)

print roc_auc_score(Y_test, Y_mlp_result)



import sys
import datetime
import argparse

sys.path.insert(0, "..")

from new_shard_sim.Transaction import Transaction

import networkx as nx
from sklearn.cluster import SpectralClustering


parser = argparse.ArgumentParser(
    description="This script will compute a graph from a transaction file and then it will use spectral clustering to find the best n number of subgraphs"
)

parser.add_argument("-n", "--number_subgraphs", type=int, default=5)
parser.add_argument("-f", "--files_prefix", type=str, default="test")
parser.add_argument("-t", "--transaction_file_path", type=str, default="test")


args = parser.parse_args()


def str_to_timestamp(time_string):
    date_day = datetime.datetime.strptime(time_string.split(" ")[0], "%Y-%m-%d")
    date_time = datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    # 1000 is due to miliseconds
    return (date_time - date_day).total_seconds() * 1000


def load_transactions_from_file(file_name):
    raw_transactions = []
    with open(file_name) as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if idx == 0:
                continue
            line_array = line.split("\t")

            if line_array[6] == "\\N" or line_array[7] == "\\N":
                continue

            raw_transactions.append(
                Transaction(
                    str_to_timestamp(line_array[3]),
                    line_array[6],
                    line_array[7],
                    float(line_array[10]),
                )
            )

    return raw_transactions


def create_transaction_graph(amount_subgraphs, transaction_list):
    transaction_graph = {}

    # initialize dictionary
    for transaction in transaction_list:
        if transaction.sender not in transaction_graph:
            transaction_graph[transaction.sender] = {}

        if transaction.recipient not in transaction_graph:
            transaction_graph[transaction.recipient] = {}

    for transaction in transaction_list:
        if transaction.recipient in transaction_graph[transaction.sender]:
            transaction_graph[transaction.sender][transaction.recipient] += 1
        elif transaction.sender in transaction_graph[transaction.recipient]:
            transaction_graph[transaction.recipient][transaction.sender] += 1
        else:
            transaction_graph[transaction.sender][transaction.recipient] = 1

    transaction_tuple_list = []
    for node in transaction_graph.keys():
        if transaction_graph[node]:
            for other_node in transaction_graph[node].keys():
                transaction_tuple_list.append((node, other_node, transaction_graph[node][other_node]))

    G = nx.Graph()

    for tuple in transaction_tuple_list:
        G.add_edge(tuple[0], tuple[1])
        G[tuple[0]][tuple[1]]["weight"] = tuple[2]

    adj = nx.adjacency_matrix(G)

    spectral_clusters = SpectralClustering(
        n_clusters=amount_subgraphs, assign_labels="discretize", affinity="precomputed"
    ).fit_predict(adj)

    return G.nodes, spectral_clusters.tolist()


def store_transaction_graph_labels(file_prefix, transaction_graph_nodes, spectral_clustering_labels):
    with open(f"{file_prefix}_txs_graph_nodes.txt", "a") as file:
        for node in transaction_graph_nodes:
            file.write(f"{node}\n")
        file.close()

    with open(f"{file_prefix}_spectral_clustering_labels.txt", "a") as file:
        for label in spectral_clustering_labels:
            file.write(f"{label}\n")
        file.close()


raw_transactions = load_transactions_from_file(args.transaction_file_path)

txs_graph_nodes, spectral_clustering_labels = create_transaction_graph(args.number_subgraphs, raw_transactions)

store_transaction_graph_labels(args.files_prefix, txs_graph_nodes, spectral_clustering_labels)

import sys
import datetime
import os

from collections import namedtuple


sys.path.insert(0, "..")

from new_shard_sim.ArchitectureGenerator import ArchitectureGenerator
from new_shard_sim.Transaction import Transaction

import networkx as nx
from sklearn.cluster import SpectralClustering


Combination = namedtuple("Combination", ["shards", "children", "levels"])


POSSIBLE_COMBINATIONS = [
    Combination(5, 2, 3),
    Combination(5, 3, 3),
    Combination(5, 5, 2),
    Combination(5, 10, 2),
    Combination(10, 3, 3),
    Combination(10, 5, 3),
    Combination(10, 10, 3),
    Combination(15, 3, 4),
    Combination(15, 5, 3),
    Combination(15, 10, 3),
    Combination(20, 3, 4),
    Combination(20, 5, 3),
    Combination(20, 10, 3),
    Combination(30, 3, 4),
    Combination(30, 5, 3),
    Combination(30, 10, 3),
    Combination(50, 5, 4),
    Combination(50, 10, 3),
]

DATA_DIR = "static_data"
OUTPUT_DATA_DIR = "precomputed_graphs"


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


def find_amount_leaf_shards(number_shards, number_children, number_levels):
    _, shard_array = ArchitectureGenerator.generate_architecture(
        number_shards=number_shards, number_children=number_children, number_levels=number_levels
    )

    return len([shard for shard in shard_array if shard.children == []])


def store_transaction_graph_labels(file_prefix, number_subgraphs, transaction_graph_nodes, spectral_clustering_labels):
    os.makedirs(f"{OUTPUT_DATA_DIR}/{str(number_subgraphs)}", exist_ok=True)

    with open(f"{OUTPUT_DATA_DIR}/{str(number_subgraphs)}/{file_prefix}_txs_graph_nodes.txt", "a") as file:
        for node in transaction_graph_nodes:
            file.write(f"{node}\n")
        file.close()

    with open(f"{OUTPUT_DATA_DIR}/{str(number_subgraphs)}/{file_prefix}_spectral_clustering_labels.txt", "a") as file:
        for label in spectral_clustering_labels:
            file.write(f"{label}\n")
        file.close()


os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)

for combination in POSSIBLE_COMBINATIONS:
    print(f"Currently processing combination {combination}")

    amount_subgraphs = find_amount_leaf_shards(combination.shards, combination.children, combination.levels)

    transaction_file_list = os.listdir(DATA_DIR)

    for transaction_file in transaction_file_list:

        print(f"Currently processing: {transaction_file}")

        raw_transactions = load_transactions_from_file(f"{DATA_DIR}/{transaction_file}")

        txs_graph_nodes, spectral_clustering_labels = create_transaction_graph(amount_subgraphs, raw_transactions)

        store_transaction_graph_labels(
            transaction_file.split(".")[0].split("_")[3], amount_subgraphs, txs_graph_nodes, spectral_clustering_labels
        )

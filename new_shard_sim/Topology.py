import string
import time
import datetime
import copy
from random import random

from new_shard_sim.Queue import Queue
from new_shard_sim.Event import Event
from new_shard_sim.Transaction import Transaction
from new_shard_sim.Constants import *

import networkx as nx
from sklearn.cluster import SpectralClustering


class Topology:

    shard_map = {}
    shard_leaf_map = {}
    shard_tree = {}

    root_shard = None

    # address -> shard_id
    address_map = {}

    raw_transactions = []

    metrics_aggregator = None

    @classmethod
    def init(cls, **args):
        if ARG_SHARDS not in args:
            raise BaseException("No shards were provided")
        cls.create_shard_map(args[ARG_SHARDS])

        if ARGS_ROOT_SHARD not in args:
            raise BaseException("No root shard provided")

        if ARGS_TXS_GRAPH_NODES_FILE_NAME not in args:
            raise BaseException("No txs graph node file name provided")

        if ARGS_TXS_SPEC_LABELS_FILE_NAME not in args:
            raise BaseException("No txs spec labels file name provided")

        cls.root_shard = args[ARGS_ROOT_SHARD]

        cls.create_shard_tree()

        if ARG_TRANSACTIONS_INPUT_FILE in args:
            cls.load_transactions_from_file(args[ARG_TRANSACTIONS_INPUT_FILE])
            if ARGS_COMPUTE_TRANSACTION_SUBGRAPHS in args:
                print("computing transaction graph from scratch")
                txs_graph_nodes, spectral_clustering_labels = cls.create_transaction_graph(cls.raw_transactions)
            else:
                print("precomputed transaction graph will be used")
                txs_graph_nodes, spectral_clustering_labels = cls.load_transaction_graph_labels(
                    args[ARGS_TXS_GRAPH_NODES_FILE_NAME], args[ARGS_TXS_SPEC_LABELS_FILE_NAME]
                )

            cls.map_spectral_cluster_labels_to_shards(txs_graph_nodes, spectral_clustering_labels)
            print(f"address map length {len(cls.address_map.keys())}")
            cls.schedule_transactions_from_file()
        else:
            print("Input file not provided")

    @classmethod
    def print_class(cls):
        search_stack = [cls.root_shard]
        string_graphic_dict = {}
        while search_stack != []:
            current_shard = search_stack.pop(0)
            string_graphic_dict[current_shard.id] = {}
            for idx, child in enumerate(current_shard.children):
                string_graphic_dict[current_shard.id][idx] = child.id
            search_stack += current_shard.children

        return f"""
            {string_graphic_dict}
        """

    @classmethod
    def create_shard_map(cls, args):
        for shard in args:
            cls.shard_map[str(shard.id)] = shard
            if not shard.children:
                cls.shard_leaf_map[str(shard.id)] = shard

    @classmethod
    def create_shard_tree(cls):
        search_stack = [cls.root_shard]
        shard_tree_dict = {}
        while search_stack != []:
            current_shard = search_stack.pop(0)
            shard_tree_dict[current_shard.id] = {}
            for idx, child in enumerate(current_shard.children):
                shard_tree_dict[current_shard.id][idx] = child.id
            search_stack += current_shard.children

        cls.shard_tree = shard_tree_dict

    @classmethod
    def set_metrics_aggregator(cls, metrics_aggregator):
        cls.metrics_aggregator = metrics_aggregator

    @classmethod
    def get_shard_from_id(cls, shard_id):
        return cls.shard_map[str(shard_id)]

    @classmethod
    def create_transaction_graph(cls, transaction_list):
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
            n_clusters=len(cls.shard_leaf_map.keys()), assign_labels="discretize", affinity="precomputed"
        ).fit_predict(adj)

        # shard_map_keys = list(cls.shard_leaf_map.keys())
        # # print(f"shard map keys {type(shard_map_keys)}")
        # for idx, node in enumerate(G.nodes):
        #     # print(type(node))
        #     # print(type(spectral_clusters.tolist()[idx]))
        #     cls.address_map[node] = shard_map_keys[(spectral_clusters.tolist())[idx]]

        # print(cls.address_map)

        return G.nodes, spectral_clusters.tolist()

    def load_transaction_graph_labels(txs_graph_file_name, txs_spec_labels_file_name):
        transaction_graph_nodes = []
        spectral_clustering_labels = []
        with open(txs_graph_file_name, "r") as file:
            for line in file.readlines():
                transaction_graph_nodes.append(line.replace("\n", ""))
            file.close()

        with open(txs_spec_labels_file_name, "r") as file:
            for line in file.readlines():
                spectral_clustering_labels.append(line.replace("\n", ""))
            file.close()

        return transaction_graph_nodes, spectral_clustering_labels

    @classmethod
    def map_spectral_cluster_labels_to_shards(cls, transaction_graph_nodes, spectral_clustering_labels):
        shard_map_keys = list(cls.shard_leaf_map.keys())

        print(f"transaction graph nodes {len(transaction_graph_nodes)}")

        print(f"spectral clustering labels length {len(spectral_clustering_labels)}")

        print(f"shard map keys length {len(shard_map_keys)}")

        for idx, node in enumerate(transaction_graph_nodes):
            cls.address_map[node] = shard_map_keys[
                # int(spectral_clustering_labels[idx]) if random() > 0.5 else idx % len(shard_map_keys)
                int(spectral_clustering_labels[idx])
            ]

    @classmethod
    def create_address_map(cls):

        pass
        # if compute subgraphs
        # cls.create_transaction_graph(cls.raw_transactions)
        # else:
        # read G and specral clusters from file

    @classmethod
    def load_transactions_from_file(cls, file_name):
        with open(file_name) as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                if idx == 0:
                    continue
                line_array = line.split("\t")

                if line_array[6] == "\\N" or line_array[7] == "\\N":
                    continue

                cls.raw_transactions.append(
                    Transaction(
                        cls.str_to_timestamp(line_array[3]),
                        line_array[6],
                        line_array[7],
                        float(line_array[10]),
                    )
                )

    def str_to_timestamp(time_string):
        date_day = datetime.datetime.strptime(time_string.split(" ")[0], "%Y-%m-%d")
        date_time = datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
        # 1000 is due to miliseconds
        return (date_time - date_day).total_seconds() * 1000

    @classmethod
    def get_shard_for_transaction(cls, transaction):
        """
        This function should return an array of shard_id(s)
        """
        # print(f"transaction sender {transaction.sender}")
        # print(f"transaction recipient {transaction.recipient}")
        if cls.address_map[transaction.sender] == cls.address_map[transaction.recipient]:
            return [cls.address_map[transaction.sender]]

        else:
            return [cls.address_map[transaction.sender], cls.address_map[transaction.recipient]]

    @classmethod
    def get_destination_shard(cls, participating_shards):
        if len(participating_shards) == 1:
            return participating_shards[0]

        else:
            return cls._lowest_common_ancestor(
                cls.shard_map[participating_shards[0]], cls.shard_map[participating_shards[1]]
            )

    def _lowest_common_ancestor(leaf_a, leaf_b):
        u = copy.deepcopy(leaf_a)
        v = copy.deepcopy(leaf_b)
        while u.depth != v.depth:
            if u.depth > v.depth:
                u = u.parent
            else:
                v = v.parent

        while u.id != v.id:
            u = u.parent
            v = v.parent

        return u.id

    @classmethod
    def schedule_transactions_from_file(cls):
        for transaction in cls.raw_transactions:
            participating_shards = cls.get_shard_for_transaction(transaction)
            destination_shard = cls.get_destination_shard(participating_shards)

            Queue.add_event(
                Event(
                    EVT_TRANSACTION_RECEIVE,
                    destination_shard,
                    transaction.timestamp,
                    transaction,
                    HANDLER_RECEIVE_TRANSACTION,
                )
            )

    @classmethod
    def reset(cls):
        cls.shard_map = {}
        cls.shard_leaf_map = {}
        cls.shard_tree = {}

        cls.root_shard = None

        # address -> shard_id
        cls.address_map = {}

        cls.raw_transactions = []

        cls.metrics_aggregator = None

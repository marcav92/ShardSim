import string
import time
import datetime
import copy

from new_shard_sim.Queue import Queue
from new_shard_sim.Event import Event
from new_shard_sim.Transaction import Transaction
from new_shard_sim.Constants import *

import networkx as nx
from sklearn.cluster import SpectralClustering


class Topology:

    shard_map = {}
    shard_leaf_map = {}

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
        cls.root_shard = args[ARGS_ROOT_SHARD]

        if ARG_TRANSACTIONS_INPUT_FILE in args:
            cls.load_transactions_from_file(args[ARG_TRANSACTIONS_INPUT_FILE])
            cls.create_address_map()
            cls.schedule_transactions_from_file()
        else:
            print("Input file not provided")

    @classmethod
    def print_class(cls):
        search_stack = [cls.root_shard]
        string_graphic_dict = {}
        while search_stack != []:
            current_shard = search_stack.pop(0)
            if current_shard.depth in string_graphic_dict:
                string_graphic_dict[current_shard.depth] += f"<{current_shard.name}:{current_shard.id}>"
            else:
                string_graphic_dict[current_shard.depth] = f"<{current_shard.name}:{current_shard.id}>"
            search_stack += current_shard.children

        return f"""
            shard_map: {cls.shard_map}
            root_shard: {string_graphic_dict}
        """

    @classmethod
    def create_shard_map(cls, args):
        for shard in args:
            cls.shard_map[str(shard.id)] = shard
            if not shard.children:
                cls.shard_leaf_map[str(shard.id)] = shard

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
            n_clusters=len(cls.shard_map.keys()), assign_labels="discretize", affinity="precomputed"
        ).fit_predict(adj)

        shard_map_keys = list(cls.shard_map.keys())
        print(f"shard map keys {type(shard_map_keys)}")
        for idx, node in enumerate(G.nodes):
            print(type(node))
            print(type(spectral_clusters.tolist()[idx]))
            cls.address_map[node] = shard_map_keys[(spectral_clusters.tolist())[idx]]

        print(cls.address_map)

    @classmethod
    def create_address_map(cls):

        cls.create_transaction_graph(cls.raw_transactions)

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

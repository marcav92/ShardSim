# Input

# precompute graph file

# prepare transactions


# Assuming that I have inputs already cooked ...

import sys
import os
from datetime import datetime
from collections import namedtuple

from numpy import number

sys.path.insert(0, "..")

from new_shard_sim.Topology import Topology
from new_shard_sim.Shard import Shard
from new_shard_sim.Engine import Engine
from new_shard_sim.Queue import Queue
from new_shard_sim.Event import Event
from new_shard_sim.MetricsAggregator import MetricsAggregator
from new_shard_sim.Logger import Logger
from new_shard_sim.Handlers import *
from new_shard_sim.Constants import *
from new_shard_sim.ArchitectureGenerator import ArchitectureGenerator


def run_permutation(
    number_shards,
    number_children,
    number_levels,
    transaction_rate,
    transactions_input_file,
):
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
    working_directory_name = (
        f"run-{number_shards}-shards-{number_children}-children-{number_levels}-levels-{transaction_rate}-txs-s"
    )
    path = f"{working_directory_name}/{dt_string}"

    os.makedirs(path)

    root_shard, shard_array = ArchitectureGenerator.generate_architecture(
        number_shards=number_shards, number_children=number_children, number_levels=number_levels
    )

    amount_subgraphs = len([shard for shard in shard_array if shard.children == []])

    print(f"root shard: {root_shard}")
    print(f"shard array: {shard_array}")

    Topology.init(
        transactions_input_file=transactions_input_file,
        txs_graph_nodes_file_name=f"precomputed_graphs/{amount_subgraphs}/{transactions_input_file.split('/')[3].split('-')[0].split('_')[3]}_txs_graph_nodes.txt",
        txs_spec_labels_file_name=f"precomputed_graphs/{amount_subgraphs}/{transactions_input_file.split('/')[3].split('-')[0].split('_')[3]}_spectral_clustering_labels.txt",
        shards=shard_array,
        root_shard=root_shard,
    )

    Logger.init(path)

    metrics_aggregator = MetricsAggregator(path)

    Topology.set_metrics_aggregator(metrics_aggregator)

    Engine().run(time_limit=500000, metrics_aggregator=metrics_aggregator)

    Topology.reset()


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

TRANSACTION_RATES = [100, 200, 300]

for combination in POSSIBLE_COMBINATIONS:
    print(f"Running simulation for {combination}")
    for transaction_rate in TRANSACTION_RATES:
        print(f"Running simulation with {transaction_rate}")
        transaction_file_list = os.listdir(f"processed_input_data/accelerated_dumps/{transaction_rate}")

        for transaction_file in transaction_file_list:
            print(f"Running simulation with tx file: {transaction_file}")
            run_permutation(
                number_shards=combination.shards,
                number_children=combination.children,
                number_levels=combination.levels,
                transaction_rate=transaction_rate,
                transactions_input_file=f"processed_input_data/accelerated_dumps/{transaction_rate}/{transaction_file}",
            )
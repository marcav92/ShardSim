import sys
import os
from datetime import datetime

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


now = datetime.now()
dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
os.mkdir(f"{dt_string}")
print(os.getcwd())

root_shard, shard_array = ArchitectureGenerator.generate_architecture(
    number_shards=10, number_children=5, number_levels=3
)

Topology.init(
    transactions_input_file="static_data/200/blockchair_ethereum_transactions_20161115-rate-200.tsv",
    txs_graph_nodes_file_name="precomputed_graphs/20161115-5c-3l-10/20161115_txs_graph_nodes.txt",
    txs_spec_labels_file_name="precomputed_graphs/20161115-5c-3l-10/20161115_spectral_clustering_labels.txt",
    shards=shard_array,
    root_shard=root_shard,
)

Logger.init(dt_string)

metrics_aggregator = MetricsAggregator(dt_string)

Topology.set_metrics_aggregator(metrics_aggregator)


Engine().run(time_limit=500000, metrics_aggregator=metrics_aggregator)

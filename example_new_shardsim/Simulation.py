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


now = datetime.now()
dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
os.mkdir(f"{dt_string}")

shard_1 = Shard(name="one", block_creation_interval=500)
shard_2 = Shard(name="two", block_creation_interval=300)
shard_3 = Shard(name="three", block_creation_interval=300)
shard_4 = Shard(name="four", block_creation_interval=100)
shard_5 = Shard(name="five", block_creation_interval=100)
shard_6 = Shard(name="six", block_creation_interval=100)
shard_7 = Shard(name="seven", block_creation_interval=100)


shard_2.define_parent(shard_1)
shard_3.define_parent(shard_1)


shard_4.define_parent(shard_2)
shard_5.define_parent(shard_2)

shard_6.define_parent(shard_3)
shard_7.define_parent(shard_3)

Topology.init(
    transactions_input_file="static_data/blockchair_ethereum_transactions_20161115.tsv",
    txs_graph_nodes_file_name="precomputed_graphs/20161115/20161115_txs_graph_nodes.txt",
    txs_spec_labels_file_name="precomputed_graphs/20161115/20161115_spectral_clustering_labels.txt",
    shards=[shard_1, shard_2, shard_3, shard_4, shard_5, shard_6, shard_7],
    root_shard=shard_1,
)

Logger.init(dt_string)

metrics_aggregator = MetricsAggregator(dt_string)

Topology.set_metrics_aggregator(metrics_aggregator)

Engine().run(time_limit=50000, metrics_aggregator=metrics_aggregator)

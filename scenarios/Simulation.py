import sys

sys.path.insert(0, "..")

from new_shard_sim.Topology import Topology
from new_shard_sim.Shard import Shard
from new_shard_sim.Engine import Engine
from new_shard_sim.Queue import Queue
from new_shard_sim.Event import Event
from new_shard_sim.MetricsAggregator import MetricsAggregator
from new_shard_sim.Handlers import *
from new_shard_sim.Constants import *


shard_1 = Shard()
shard_2 = Shard()
shard_3 = Shard()

shard_2.define_parent(shard_1)
shard_3.define_parent(shard_1)


Topology.init(
    transactions_input_file="static_data/data",
    shards=[shard_1, shard_2, shard_3],
    root_shard=shard_1,
)

metrics_aggregator = MetricsAggregator()

Topology.set_metrics_aggregator(metrics_aggregator)

Engine().run(time_limit=100000000, metrics_aggregator=metrics_aggregator)

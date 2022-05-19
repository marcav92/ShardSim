from shard_sim.Constants import *


class Topology:
    def __init__(self):
        self.environment = {
            # TODO: Add the capability of specifying several types of shards
            "reference_shards": [],
            "worker_shards": [],
            "nodes": [],
        }
        # address -> shard
        self.addresses_map = {}

    def get_nodes(self):
        return self.environment["nodes"]

    def get_worker_shards(self):
        return self.environment["worker_shards"]

    def create_environment(self, shard_array):

        for shard in shard_array:
            if shard.type == REFERENCE:
                self.environment["reference_shards"].append(shard)

            if shard.type == WORKER:
                self.environment["worker_shards"].append(shard)

        for shard in shard_array:
            self.environment[shard.id] = shard
            self.environment[f"{shard.id}_nodes"] = shard.nodes
            self.environment["nodes"].append(shard.nodes)

            for node in shard.nodes:
                self.environment[node.id] = node

        return self.environment

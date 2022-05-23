from shard_sim.Constants import *


class Topology:
    def __init__(self):
        self.environment = {
            # TODO: Add the capability of specifying several types of shards
            REFERENCE: [],
            WORKER: [],
            "nodes": [],
        }
        # address -> shard
        self.addresses_map = {}

    def get_nodes(self):
        return self.environment["nodes"]

    def get_shards(self, type):
        return self.environment[type]

    def get_shard_by_id(self, shard_id):
        return self.environment[shard_id]

    def create_environment(self, shard_array):

        for shard in shard_array:
            if shard.type == REFERENCE:
                self.environment[REFERENCE].append(shard)

            if shard.type == WORKER:
                self.environment[WORKER].append(shard)

        for shard in shard_array:
            self.environment[shard.id] = shard
            self.environment[f"{shard.id}_nodes"] = shard.nodes
            self.environment["nodes"].append(shard.nodes)

            for node in shard.nodes:
                self.environment[node.id] = node

        return self.environment

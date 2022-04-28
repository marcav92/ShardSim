from shard_sim.Shard import Shard
from shard_sim.Node import NodeL1, NodeL2BasicRivet
import shard_sim.Constants as c

class Topology():

    environment = {
        'shards': [],
        'nodes': []
    }

    def setup_topology():
        shard_1 = Shard('MyShard')

        node_1 = NodeL2BasicRivet(c.WORKER,'one')
        node_2 = NodeL2BasicRivet(c.WORKER,'two')
        node_3 = NodeL2BasicRivet(c.WORKER,'three')

        shard_1.add_node(node_1)
        shard_1.add_node(node_2)
        shard_1.add_node(node_3)

        shard_1.define_neighbors(node_1, node_2)
        shard_1.define_neighbors(node_1, node_3)

        shard_2 = Shard('MyShard2')

        node_4 = NodeL2BasicRivet(c.WORKER,'four')
        node_5 = NodeL2BasicRivet(c.WORKER,'five')
        node_6 = NodeL2BasicRivet(c.WORKER,'six')

        shard_2.add_node(node_4)
        shard_2.add_node(node_5)
        shard_2.add_node(node_6)

        shard_2.define_neighbors(node_4, node_5)
        shard_2.define_neighbors(node_4, node_6)

        Shard.define_shard_neighbors(shard_1, shard_2, 3)

        Topology.create_environment([shard_1, shard_2])

    def create_environment(shard_array):

        Topology.environment['shards'] = shard_array

        for shard in shard_array:
            Topology.environment[shard.id] = shard
            Topology.environment[f"{shard.id}nodes"] = shard.nodes
            Topology.environment['nodes'].append(shard.nodes)

            for node in shard.nodes:
                Topology.environment[node.id] = node

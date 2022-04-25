from shard_sim.Shard import Shard
from shard_sim.Node import NodeL1

class Topology():

    def __init__(self):
        pass

    def setup_topology():
        shard_1 = Shard('MyShard')

        node_1 = NodeL1('one')
        node_2 = NodeL1('two')
        node_3 = NodeL1('three')

        shard_1.add_node(node_1)
        shard_1.add_node(node_2)
        shard_1.add_node(node_3)

        shard_1.define_neighbors(node_1, node_2)
        shard_1.define_neighbors(node_1, node_3)

        return shard_1
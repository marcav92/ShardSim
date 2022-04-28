import uuid

class Shard():
    
    def __init__(self, id=None):
        self.id = id if id else uuid.uuid4()
        self.nodes = []
        self.node_graph = {}

    def __repr__(self):
        return f'''
            node_graph  :   {self.node_graph}    
        '''
    def define_shard_neighbors(shard_a, shard_b, number_of_connections):
        if number_of_connections < len(shard_a.nodes):
            raise Exception('Shard doesnt have enough nodes for the amount of connections specified')
        for idx, node in enumerate(shard_a.nodes):
            node.add_crossshard_neighbor(shard_b.nodes[idx])
            shard_b.nodes[idx].add_crossshard_neighbor(node)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)
            self.node_graph[str(node.id)] = []
        else:
            print('provided node already exists')

    def define_neighbors(self, node_i, node_j):
        if str(node_i.id) not in self.node_graph or \
            str(node_j.id) not in self.node_graph:
            print(f'one or more nodes are not defined as a node of this shard')
        else:
            if str(node_j.id) not in self.node_graph[str(node_i.id)]:
                self.node_graph[str(node_i.id)].append(str(node_j.id))
                self.node_graph[str(node_j.id)].append(str(node_i.id))

                node_i.set_membership(self.id)
                node_i.add_intrashard_neighbor(node_j)

                node_j.set_membership(self.id)
                node_j.add_intrashard_neighbor(node_i)


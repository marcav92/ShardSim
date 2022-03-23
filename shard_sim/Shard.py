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
                node_i.add_neighbor(node_j)

                node_j.set_membership(self.id)
                node_j.add_neighbor(node_i)
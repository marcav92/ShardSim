import uuid

class Shard():
    
    def __init__(self, type, id=None):
        self.type = type
        self.id = id if id else uuid.uuid4()
        self.nodes = []
        self.node_graph = {}
        self.account_set = {}

    def __repr__(self):
        return f'''
            node_graph  :   {self.node_graph}    
        '''

    def get_nodes(self):
        return self.nodes
        
    def define_shard_neighbors(shard_a, shard_b, number_of_connections):
        if number_of_connections > len(shard_a.nodes):
            raise Exception('Shard doesnt have enough nodes for the amount of connections specified')
        for idx, node in enumerate(shard_a.nodes):
            node.add_crossshard_neighbor(shard_b.nodes[idx])
            shard_b.nodes[idx].add_crossshard_neighbor(node)

    def add_node(self, node):
        if node not in self.nodes:
            node.define_shard(self)
            self.nodes.append(node)
            self.node_graph[str(node.id)] = []
        else:
            print('provided node already exists')

    def add_account(self, account):
        self.account_set[account] = 1

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


class Shard_Hot_Stuff(Shard):

    def __init__(self, type, id=None):
        super().__init__(type, id)
        self.view_id_map = {}
        self.f_value = 0
        self.n_value = 0

    def get_n_f_value(self):
        return self.n_value - self.f_value

    def assign_view_numbers(self):
        for idx, node in enumerate(self.nodes):
            node.set_view_number(idx)
            self.view_id_map[idx]=node.id

    def calculate_maximum_amount_faulty_nodes(self):
        #check if number of replicas yields an integer number of maximum faulty nodes n = 3f + 1
        if ((len(self.nodes)-1) % 3 != 0):
            raise Exception("Amount of replicas in shard doesn't comply with n=3f+1")

        self.f_value = (len(self.nodes)-1)//3

    def add_node_hot_stuff(self, node):
        self.add_node(node)
        self.n_value += 1
        self.assign_view_numbers()

import uuid
from shard_sim.Block import Block
from shard_sim.Event import Event
from shard_sim.Queue import Queue

class Node():

    def __init__(self, id=None):
        self.id = id if id else uuid.uuid4()
        self.blockchain = []
        self.transactionsPool = []
        self.membership = ''
        self.neighbors = []

    def __repr__(self):
        return f'''
            id              :   {self.id}
            blockchain      :   {self.blockchain}
            transactionPool :   {self.transactionsPool}
            neighbors       :   {self.neighbors}
        '''
    """
        original methods
    """
    def generate_genesis_block(nodes_list):
        for node in nodes_list:
            node.blockchain.append(Block())

    def get_last_block(self):
        return self.blockchain[len(self.blockchain)-1]

    def get_blockchain_length(self):
        return len(self.blockchain)-1

    def reset_state(nodes_list):
        for node in nodes_list:
            node.blockchain=[]
            node.transactionsPool=[]

    def add_neighbor(self,node):
        self.neighbors.append(node)
        
    def set_membership(self, shard_id):
        self.membership = shard_id

    def propagate_transaction(self, event):
        print(f'propagating transaction {event.data}')

        if event.id not in self.transactionsPool:
            for node in self.neighbors:
                Queue.add_event(Event('receive_transaction', node.id, event.time+0.5, event.data, event.id))

            self.transactionsPool.append(event.id)
import uuid
from shard_sim.Block import Block
from shard_sim.Event import Event
from shard_sim.Queue import Queue

class SimulationLogger():
    def __init__(self):
        self.event_log = []
    
    def log_event(self, event):
        self.event_log.append(event)




class NodeL1(SimulationLogger):

    def __init__(self, id=None):
        super().__init__()
        self.id = id if id else uuid.uuid4()
        self.transactions_pool = []
        self.membership = ''
        self.intrashard_neighbors = []
        self.crossshard_neighbors = []

    def __repr__(self):
        return f'''
            id                  :   {self.id}
            blockchain          :   {self.blockchain}
            transactionPool     :   {self.transactions_pool}
            intrashard neighbors:   {self.intrashard_neighbors}
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
            node.transactions_pool=[]

    def add_intrashard_neighbor(self,node):
        self.intrashard_neighbors.append(node)
        
    def set_membership(self, shard_id):
        self.membership = shard_id

    def propagate_transaction(self, event):
        #print(f'propagating transaction {event.data}')

        #events could have several types i.e transaction, block
        if event.data.id not in [transaction.id for transaction in self.transactions_pool]:
            for node in self.intrashard_neighbors:
                #create function to calculate time delay
                Queue.add_event(Event('receive_transaction', node.id, event.time+0.5, event.data, event.id))
                self.log_event(event)
            self.transactions_pool.append(event.data)
    


class NodeL2BasicRivet(NodeL1):

    def __init__(self, id = None):
        super().__init__(id)
        self.blockchain = []

    def worker_shard_leader():
        pass


    #implement consensus as a factory
    #https://stackoverflow.com/questions/40898482/defining-method-of-class-in-if-statement

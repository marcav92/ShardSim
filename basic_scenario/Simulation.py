import sys
sys.path.insert(0,"..")

from shard_sim.SetupTopology import Topology
from shard_sim.Client import Client
from shard_sim.Event import Event
from shard_sim.Queue import Queue
from shard_sim.Transaction import Transaction
from shard_sim.EventHandler import EventHandler
from shard_sim.Node import NodeL2BasicRivet
from shard_sim.Shard import Shard
from shard_sim.TransactionPreprocessor import TransactionPreprocessor as Preprocessor
import shard_sim.Constants as c

#there needs to be a setup phase
shard_1 = Shard(c.WORKER,'MyShard')

node_1 = NodeL2BasicRivet(c.WORKER,'one')
node_2 = NodeL2BasicRivet(c.WORKER,'two')
node_3 = NodeL2BasicRivet(c.WORKER,'three')

shard_1.add_node(node_1)
shard_1.add_node(node_2)
shard_1.add_node(node_3)

shard_1.define_neighbors(node_1, node_2)
shard_1.define_neighbors(node_1, node_3)

shard_2 = Shard(c.REFERENCE,'MyShard2')

node_4 = NodeL2BasicRivet(c.WORKER,'four')
node_5 = NodeL2BasicRivet(c.WORKER,'five')
node_6 = NodeL2BasicRivet(c.WORKER,'six')

shard_2.add_node(node_4)
shard_2.add_node(node_5)
shard_2.add_node(node_6)

shard_2.define_neighbors(node_4, node_5)
shard_2.define_neighbors(node_4, node_6)

shard_3 = Shard(c.WORKER,'MyShard3')

node_7 = NodeL2BasicRivet(c.WORKER,'seven')
node_8 = NodeL2BasicRivet(c.WORKER,'eight')
node_9 = NodeL2BasicRivet(c.WORKER,'nine')

shard_3.add_node(node_7)
shard_3.add_node(node_8)
shard_3.add_node(node_9)

shard_3.define_neighbors(node_7, node_8)
shard_3.define_neighbors(node_7, node_9)

Shard.define_shard_neighbors(shard_3, shard_2, 3)

topology = Topology()

environment = topology.create_environment([shard_1, shard_2, shard_3])

preprocessor = Preprocessor()

preprocessor.load_transactions_from_file('../shard_sim/static_data/data')

preprocessor.assign_accounts_to_shards(topology)

#scheduling

my_client = Client('me')
now = 0

#loading the queue with some initial stimulus
my_client.send_transaction(Transaction(0, '0x123', '0x456'), 'one', 0, 'hello')
my_client.send_transaction(Transaction(0, '0xABC', '0x456'), 'one', 0.5, 'ciao')
my_client.send_transaction(Transaction(0, '0x1EF', '0x456'), 'two', 1.5, 'hallo')
my_client.send_transaction(Transaction(0, '0x123', '0x789'), 'three', 2.5, 'hola')
my_client.send_transaction(Transaction(0, '0x123', '0x789'), 'one', 3.5, 'bonjour')
Queue.add_event(Event(c.EVT_WORKER_CREATE_BLOCK, 'one', 6, 'create', 'genesis'))



#run phase
while (not Queue.isEmpty()):
    event = Queue.get_next_event()
    now = event.time
    EventHandler.handle_event(event, environment)



#debug

# print(environment)

# Shard related

print(f"shard three accounts {shard_3.account_set}")

# print(f"blockchain node one {environment['one'].blockchain}")
# print(f"blockchain node two {environment['two'].blockchain}")

# print(f'Node two event log {my_shard.nodes[1].event_log}')
# print(f'Node three event log {my_shard.nodes[2].event_log}')

# print(f'Node one transactions pool {my_shard.nodes[0].transactions_pool}')
# print(f'Node two transactions pool {my_shard.nodes[1].transactions_pool}')
# print(f'Node three transactions pool {my_shard.nodes[2].transactions_pool}')

#store metrics phase







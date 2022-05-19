import sys
sys.path.insert(0,"..")

from shard_sim.SetupTopology import Topology
from shard_sim.Client import Client
from shard_sim.Event import Event
from shard_sim.Queue import Queue
from shard_sim.Transaction import Transaction
from shard_sim.EventHandler import EventHandler
from shard_sim.Node import NodeL2BasicHotStuff
from shard_sim.Shard import Shard, Shard_Hot_Stuff
from shard_sim.TransactionPreprocessor import TransactionPreprocessor as Preprocessor
import shard_sim.Constants as c
import time

#there needs to be a setup phase
shard_1 = Shard_Hot_Stuff(c.WORKER,'MyShard')

node_1 = NodeL2BasicHotStuff('one')
node_2 = NodeL2BasicHotStuff('two')
node_3 = NodeL2BasicHotStuff('three')
node_3_1 = NodeL2BasicHotStuff('three_1')

shard_1.add_node_hot_stuff(node_1)
shard_1.add_node_hot_stuff(node_2)
shard_1.add_node_hot_stuff(node_3)
shard_1.add_node_hot_stuff(node_3_1)

shard_1.define_neighbors(node_1, node_2)
shard_1.define_neighbors(node_1, node_3)

shard_1.calculate_maximum_amount_faulty_nodes()

shard_2 = Shard_Hot_Stuff(c.REFERENCE,'MyShard2')

node_4 = NodeL2BasicHotStuff('four')
node_5 = NodeL2BasicHotStuff('five')
node_6 = NodeL2BasicHotStuff('six')
node_6_1 = NodeL2BasicHotStuff('six_1')

shard_2.add_node_hot_stuff(node_4)
shard_2.add_node_hot_stuff(node_5)
shard_2.add_node_hot_stuff(node_6)
shard_2.add_node_hot_stuff(node_6_1)

shard_2.define_neighbors(node_4, node_5)
shard_2.define_neighbors(node_4, node_6)

shard_2.calculate_maximum_amount_faulty_nodes()

shard_3 = Shard_Hot_Stuff(c.WORKER,'MyShard3')

node_7 = NodeL2BasicHotStuff('seven')
node_8 = NodeL2BasicHotStuff('eight')
node_9 = NodeL2BasicHotStuff('nine')
node_9_1 = NodeL2BasicHotStuff('nine_1')

shard_3.add_node_hot_stuff(node_7)
shard_3.add_node_hot_stuff(node_8)
shard_3.add_node_hot_stuff(node_9)
shard_3.add_node_hot_stuff(node_9_1)

shard_3.define_neighbors(node_7, node_8)
shard_3.define_neighbors(node_7, node_9)

shard_3.calculate_maximum_amount_faulty_nodes()

Shard.define_shard_neighbors(shard_3, shard_2, 3)

topology = Topology()

environment = topology.create_environment([shard_1, shard_2, shard_3])

preprocessor = Preprocessor()

preprocessor.load_transactions_from_file('./static_data/data')

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

#trigger hotstuff

Queue.add_event(Event(c.EVT_REFERENCE_HOT_STUFF_MESSAGE,'four',0, {
    "type": c.EVT_REFERENCE_HOT_STUFF_NEW_VIEW_MESSAGE,
    "current_view_number": 1
}))

Queue.add_event(Event(c.EVT_REFERENCE_HOT_STUFF_MESSAGE,'four',0, {
    "type": c.EVT_REFERENCE_HOT_STUFF_NEW_VIEW_MESSAGE,
    "current_view_number": 1
}))

Queue.add_event(Event(c.EVT_REFERENCE_HOT_STUFF_MESSAGE,'four',0, {
    "type": c.EVT_REFERENCE_HOT_STUFF_NEW_VIEW_MESSAGE,
    "current_view_number": 1
}))



#run phase
while (not Queue.isEmpty()):
    event = Queue.get_next_event()
    now = event.time
    print(event)
    time.sleep(2)
    EventHandler.handle_event(event, environment)



#debug

# print(environment)

# Shard related

# print(f"shard three accounts {shard_3.account_set}")

# print(f"blockchain node one {environment['one'].blockchain}")
# print(f"blockchain node two {environment['two'].blockchain}")

# print(f'Node two event log {my_shard.nodes[1].event_log}')
# print(f'Node three event log {my_shard.nodes[2].event_log}')

# print(f'Node one transactions pool {my_shard.nodes[0].transactions_pool}')
# print(f'Node two transactions pool {my_shard.nodes[1].transactions_pool}')
# print(f'Node three transactions pool {my_shard.nodes[2].transactions_pool}')

#store metrics phase







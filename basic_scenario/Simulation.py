import sys

sys.path.insert(0, "..")

from shard_sim.SetupTopology import Topology
from shard_sim.Client import Client
from shard_sim.Event import Event
from shard_sim.Queue import Queue
from shard_sim.Transaction import Transaction
from shard_sim.EventHandler import EventHandler
from shard_sim.Node import NodeL2BasicHotStuff
from shard_sim.Shard import Shard, Shard_Hot_Stuff, Shard_Rivet
from shard_sim.TransactionPreprocessor import TransactionPreprocessor as Preprocessor
from shard_sim.Configuration import Config
from shard_sim.Constants import *
import time

Config.init(worker_block_interval=600)

shard_1 = Shard_Rivet(WORKER, 7)
shard_2 = Shard_Rivet(WORKER, 7)
shard_3 = Shard_Rivet(REFERENCE, 10)


shard_1.define_shard_neighbor(shard_3, 4)
shard_2.define_shard_neighbor(shard_3, 4)

topology = Topology()

environment = topology.create_environment([shard_1, shard_2, shard_3])

preprocessor = Preprocessor()

preprocessor.load_transactions_from_file("./static_data/data")

preprocessor.assign_accounts_to_shards(topology)

# scheduling

my_client = Client("me")
now = 0

# loading the queue with some initial stimulus
# my_client.send_transaction(Transaction(0, "0x123", "0x456"), "one", 0, "hello")
# my_client.send_transaction(Transaction(0, "0xABC", "0x456"), "one", 0.5, "ciao")
# my_client.send_transaction(Transaction(0, "0x1EF", "0x456"), "two", 1.5, "hallo")
# my_client.send_transaction(Transaction(0, "0x123", "0x789"), "three", 2.5, "hola")
# my_client.send_transaction(Transaction(0, "0x123", "0x789"), "one", 3.5, "bonjour")

# trigger hotstuff

Shard_Hot_Stuff.create_event(
    topology,
    shard_3.get_id(),
    EVT_REFERENCE_RIVET_MESSAGE,
    0,
    {"type": EVT_REFERENCE_RIVET_NEW_VIEW_MESSAGE, "current_view_number": 1},
)


# run phase
while not Queue.isEmpty():
    event = Queue.get_next_event()
    now = event.time
    print(event)
    time.sleep(2)
    EventHandler.handle_event(event, environment)


# debug

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

# store metrics phase

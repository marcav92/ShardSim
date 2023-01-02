import sys

sys.path.insert(0, "..")

from shard_sim.SetupTopology import Topology
from shard_sim.Client import Client
from shard_sim.Event import Event
from shard_sim.Queue import Queue
from shard_sim.Transaction import Transaction
from shard_sim.EventHandler import EventHandler
from shard_sim.Node import NodeL2BasicHotStuff
from shard_sim.Shard import Shard_Rivet
from shard_sim.TransactionPreprocessor import TransactionPreprocessor as Preprocessor
from shard_sim.Configuration import Config
from shard_sim.Constants import *
from shard_sim.TransactionScheduler import TransactionScheduler
from shard_sim.Logger import Logger
import time

logger = Logger("simulation_log", ["WORKER_RIVET_PROPOSAL_MESSAGE", "WORKER_RIVET_CERTIFICATION_MESSAGE", "WORKER_RIVET_CERTIFICATION_VOTE_MESSAGE"])

Config.init(worker_block_interval=600)

shard_1 = Shard_Rivet(WORKER, 7)
shard_2 = Shard_Rivet(WORKER, 7)
shard_3 = Shard_Rivet(REFERENCE, 10)


shard_1.define_shard_neighbor(shard_3, 4)
shard_2.define_shard_neighbor(shard_3, 4)

topology = Topology()

environment = topology.create_environment(shard_1, shard_2, shard_3)

preprocessor = Preprocessor()

# preprocessor.load_transactions_from_file("./static_data/data")

# preprocessor.assign_accounts_to_shards(topology)

# TransactionScheduler.add_transaction_events_to_queue(preprocessor.raw_transactions, topology)


# trigger hotstuff


Shard_Rivet.create_event_worker(
    topology,
    shard_1.get_id(),
    EVT_REFERENCE_RIVET_MESSAGE,
    105,
    {"type": EVT_WORKER_RIVET_PROPOSAL_MESSAGE, "current_view_number": 0},
)

# Shard_Rivet.create_event_worker(
#     topology,
#     shard_2.get_id(),
#     EVT_REFERENCE_RIVET_MESSAGE,
#     100,
#     {"type": EVT_WORKER_RIVET_PROPOSAL_MESSAGE, "current_view_number": 1},
# )

# Shard_Rivet.create_event_reference(
#     topology,
#     shard_3.id,
#     EVT_REFERENCE_RIVET_MESSAGE,
#     0,
#     {"type": EVT_REFERENCE_RIVET_NEW_VIEW_MESSAGE, "current_view_number": 1},
# )

now = 0
event_count = 0
# run phase
while not Queue.isEmpty() and now < 8600:
    event_count += 1
    event = Queue.get_next_event()
    now = event.time
    logger.append_log(event)
    # print(str(event_count)+":"+str(event))
    # time.sleep(0.5)
    EventHandler.handle_event(event, environment)

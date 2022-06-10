# reference of queue
# should be able to read csv with transactions
# should schedule block generation depending on a list of nodes from the simulation
# should schedule block generation based on a specified frequency
# should schedule block generation with jitter

# should be able to handle several frequencies depending if the node belongs to
# reference shard or worker shard.

# might need to schedule data reception events

import time
import datetime
from random import randint
from shard_sim.Event import Event
from shard_sim.Queue import Queue
from shard_sim.SetupTopology import Topology
from shard_sim.Shard import Shard_Rivet
from shard_sim.Transaction import Transaction
from shard_sim.Constants import *


class TransactionScheduler:
    def calculate_simulation_duration(transactions):
        return transactions[-1]["timestamp"] - transactions[0]["timestamp"]

    def add_transaction_events_to_queue(transactions, topology: Topology):
        worker_shards_array = topology.get_shards(WORKER)

        for transaction in transactions:
            sender_shard = topology.addresses_map[transaction["sender"]]
            recipient_shard = topology.addresses_map[transaction["recipient"]]

            if sender_shard == recipient_shard:
                destination_shard = worker_shards_array[sender_shard]
                nodes = destination_shard.get_nodes()
                selected_node = randint(0, len(nodes) - 1)
                event_time = transaction["timestamp"] - transactions[0]["timestamp"]
                event_data = Transaction(
                    event_time, transaction["sender"], transaction["recipient"], transaction["amount"]
                )
                Queue.add_event(
                    Event(
                        EVT_RECEIVE_TRANSACTION,
                        nodes[selected_node].id,
                        event_time,
                        event_data,
                    )
                )

            else:
                reference_shard: Shard_Rivet = topology.get_shards(REFERENCE)
                nodes = reference_shard[0].get_nodes()
                selected_node = randint(0, len(nodes) - 1)
                event_time = transaction["timestamp"] - transactions[0]["timestamp"]
                event_data = Transaction(
                    event_time, transaction["sender"], transaction["recipient"], transaction["amount"]
                )
                Queue.add_event(
                    Event(
                        EVT_RECEIVE_TRANSACTION,
                        nodes[selected_node].id,
                        event_time,
                        event_data,
                    )
                )

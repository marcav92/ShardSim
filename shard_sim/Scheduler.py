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
from shard_sim.Transaction import Transaction
from shard_sim.Constants import *


class Scheduler:
    def __init__(
        self,
        # environment,
        # reference_node_frequency,
        # worker_node_frequency,
        # with_jitter,
        # TODO I need to create types of scheduler as different protocols
        # will need different schedules
    ):
        pass

    def calculate_simulation_duration(self, transactions):
        return transactions[-1]["timestamp"] - transactions[0]["timestamp"]

    def add_transaction_events_to_queue(self, transactions, topology):
        worker_shards_array = topology.get_worker_shards()

        for transaction in transactions:
            sender_shard = topology.addresses_map[transaction["sender"]]
            recipient_shard = topology.addresses_map[transaction["recipient"]]

            if sender_shard == recipient_shard:
                # intrashard transaction
                # find random node from shard
                # find timestamp offset
                # create transaction object with the data
                # no event id is needed
                destination_shard = worker_shards_array[sender_shard]
                nodes = destination_shard.get_nodes()
                selected_node = randint(0, len(nodes))
                event_time = transaction["timestamp"] - transactions[0]["timestamp"]
                event_data = Transaction(
                    0, transaction["sender"], transaction["recipient"]
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
                # crossshard transaction
                # TODO there are a couple of details that I still need to figure out for
                # TODO crossshard transactions
                # it will be necessary to take in consideration how will this happen
                # in a multilayer topology
                pass

    # def add_create_block_events_to_queue(self,transactions, topology, period):
    #     #this is currently going to work for all nodes
    #     #TODO add the posibility to spcify different frequencies per shard/layer
    #     node_array = topology.get_nodes()

    #     for node in node_array:
    #         sim_time=0
    #         simulation_duration = self.calculate_simulation_duration(transactions)
    #         while sim_time < simulation_duration:
    #             if node.shard_type == c.WORKER:
    #                 Queue.add_event(Event(c.EVT_WORKER_CREATE_BLOCK, node.id, sim_time, 'create_worker_block'))
    #             elif node.shard_type == c.REFERENCE:
    #                 Queue.add_event(Event(c.EVT_REFERENCE_CREATE_BLOCK, node.id, sim_time, 'create_reference_block'))

    #             #TODO define other random functions
    #             jitter = randint(0, period//10)
    #             sim_time += period + jitter if jitter > period//20 else period - jitter

    def add_create_block_events_to_queue(self, topology):

        node_array = topology.get_nodes()

        for node in node_array:
            jitter = randint(0, 60)  # it may be necessary to make this a parameter
            if node.shard_type == WORKER:
                Queue.add_event(
                    Event(EVT_WORKER_CREATE_BLOCK, node.id, 0, "create_worker_block")
                )
            elif node.shard_type == REFERENCE:
                Queue.add_event(
                    Event(
                        EVT_REFERENCE_CREATE_BLOCK, node.id, 0, "create_reference_block"
                    )
                )

    def add_worker_commit_block_event(self):
        pass

from shard_sim.Event import Event
from shard_sim.Queue import Queue
from shard_sim.Constants import *


class Client:
    def __init__(self, id):
        self.id = id

    def send_transaction(self, transaction_data, target_node, time, event_id=None):
        Queue.add_event(
            Event(EVT_SEND_TRANSACTION, target_node, time, transaction_data, event_id)
        )

import time
from shard_sim.Event import Event
from shard_sim.Queue import Queue

class Client():

    def __init__(self, id):
        self.id = id

    def send_transaction(self, transaction_data):
        Queue.add_event(Event('send_transaction','client', time.time(), transaction_data))
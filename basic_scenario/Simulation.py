from multiprocessing.connection import Client
import sys
sys.path.insert(0,"..")

from Topology import Topology
from shard_sim.Client import Client
from shard_sim.Event import Event
from shard_sim.Queue import Queue

#there needs to be a setup phase
my_shard = Topology.setup_topology()
my_client = Client('me')

#loading the queue with some initial stimuli
my_client.send_transaction({
    'target_node': 'one',
    'amount': 50
})

my_client.send_transaction({
    'target_node': 'two',
    'amount': 100
})


def handle_event(event):
    if event.type == 'send_transaction':

        Queue.add_event(Event('receive_transaction', event.data['target_node'], event.time+0.5, event.data))

    elif event.type == 'receive_transaction':

        for node in my_shard.nodes:
            # print(node)
            if node.id == event.node:
                node.propagate_transaction(event)

#run phase
while (not Queue.isEmpty()):
    event = Queue.get_next_event()
    print(Queue.size())
    handle_event(event)

#store metrics phase







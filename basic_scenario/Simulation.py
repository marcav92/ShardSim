import sys
sys.path.insert(0,"..")

from Topology import Topology
from shard_sim.Client import Client
from shard_sim.Event import Event
from shard_sim.Queue import Queue
from shard_sim.Transaction import Transaction

#there needs to be a setup phase
my_shard = Topology.setup_topology()
my_client = Client('me')
now = 0

#loading the queue with some initial stimuli
my_client.send_transaction(Transaction(0, '0x123', '0x456'), 'one', 0, 'hello')
my_client.send_transaction(Transaction(0, '0xABC', '0x456'), 'one', 0.5, 'ciao')
my_client.send_transaction(Transaction(0, '0x1EF', '0x456'), 'two', 1.5, 'hallo')
my_client.send_transaction(Transaction(0, '0x123', '0x789'), 'three', 2.5, 'hola')
my_client.send_transaction(Transaction(0, '0x123', '0x789'), 'one', 3.5, 'bonjour')


def handle_event(event):
    if event.type == 'send_transaction':
        Queue.add_event(Event('receive_transaction', event.node, event.time+0.5, event.data, event.id))

    elif event.type == 'receive_transaction':
        for node in my_shard.nodes:
            if node.id == event.node:
                node.propagate_transaction(event)

#run phase
while (not Queue.isEmpty()):
    event = Queue.get_next_event()
    now = event.time
    print(f'{now} - {event}')
    handle_event(event)

#debug
# print(f'Node one event log {my_shard.nodes[0].event_log}')
# print(f'Node two event log {my_shard.nodes[1].event_log}')
# print(f'Node three event log {my_shard.nodes[2].event_log}')

# print(f'Node one transactions pool {my_shard.nodes[0].transactions_pool}')
# print(f'Node two transactions pool {my_shard.nodes[1].transactions_pool}')
# print(f'Node three transactions pool {my_shard.nodes[2].transactions_pool}')

#store metrics phase







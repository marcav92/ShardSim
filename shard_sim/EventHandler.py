import shard_sim.Constants as c
from shard_sim.Queue import Queue
from shard_sim.Event import Event

class EventHandler():

    def handle_event(event, sim_environment):
        if event.type == c.EVT_SEND_TRANSACTION:
            Queue.add_event(Event(c.EVT_RECEIVE_TRANSACTION, event.node, event.time+0.5, event.data, event.id))

        elif event.type == c.EVT_RECEIVE_TRANSACTION:
            sim_environment[event.node].receive_event_L1(event)

        elif event.type == c.EVT_WORKER_CREATE_BLOCK:
            sim_environment[event.node].receive_event_L2(event)

        elif event.type == c.EVT_WORKER_VERIFY_BLOCK:
            sim_environment[event.node].receive_event_L2(event)
        # else:
        #     raise Exception('Unkown event')
                
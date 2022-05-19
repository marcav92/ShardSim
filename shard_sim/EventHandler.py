from shard_sim.Constants import *
from shard_sim.Queue import Queue
from shard_sim.Event import Event

class EventHandler():

    def handle_event(event, sim_environment):
        if event.type == EVT_SEND_TRANSACTION:
            Queue.add_event(Event(EVT_RECEIVE_TRANSACTION, event.node, event.time+0.5, event.data, event.id))

        #TODO: this implementation should not go here because this is specific to a protocol
        elif event.type == EVT_RECEIVE_TRANSACTION:
            sim_environment[event.node].receive_event_L1(event)

        elif event.type == EVT_REFERENCE_HOT_STUFF_MESSAGE:
            sim_environment[event.node].receive_event_L2(event)
                
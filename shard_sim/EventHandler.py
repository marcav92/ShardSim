from shard_sim.Constants import *
from shard_sim.Queue import Queue
from shard_sim.Event import Event


class EventHandler:
    def handle_event(event, sim_environment):

        # TODO: this implementation should not go here because this is specific to a protocol
        if event.type == EVT_RECEIVE_TRANSACTION:
            sim_environment[event.node_id].receive_event_L1(event)

        elif event.type == EVT_REFERENCE_HOT_STUFF_MESSAGE:
            sim_environment[event.node_id].receive_event_L2(event)

        elif event.type == EVT_REFERENCE_RIVET_MESSAGE:
            sim_environment[event.node_id].receive_event_L2(event)

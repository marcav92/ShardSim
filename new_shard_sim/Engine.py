import time
from new_shard_sim.Queue import Queue
from new_shard_sim.Event import Event
from new_shard_sim.Constants import *
from new_shard_sim.Logger import Logger


class Engine:
    handlers = {}

    def __init__(self):
        self.now = 0

    def run(self, time_limit, metrics_aggregator):
        while not Queue.isEmpty() and self.now < time_limit:
            event: Event = Queue.get_next_event()
            self.now = event.time
            if DEBUG:
                Logger.log_message(ENGINE, self.now, event, event.shard_id)
                # time.sleep(0.5)
            if event.handler_name in Engine.handlers:
                Engine.handlers[event.handler_name](event)
            else:
                raise BaseException("handler name is not registered")

        metrics_aggregator.dump_metrics("profile")
        print("Queue is empty, ending simulation")

    @classmethod
    def register_handler(cls, handler_name, handler):
        cls.handlers[handler_name] = handler

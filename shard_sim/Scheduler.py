#reference of queue
#should be able to read csv with transactions
#should schedule block generation depending on a list of nodes from the simulation
#should schedule block generation based on a specified frequency
#should schedule block generation with jitter

#should be able to handle several frequencies depending if the node belongs to
#reference shard or worker shard.

#might need to schedule data reception events

import time
import datetime
from shard_sim.Event import Event
from shard_sim.Queue import Queue
import shard_sim.Constants as c

class Scheduler():

    def __init__(self, 
        # environment,
        # reference_node_frequency,
        # worker_node_frequency,
        # with_jitter,
        ):
        self.raw_transactions = []

    def load_transactions_from_file(self, file_name):
        with open(file_name) as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                if idx == 0:
                    continue
                line_array = line.split('\t')
                self.raw_transactions.append({
                    'timestamp': Scheduler.str_to_timestamp(line_array[3]),
                    'sender': line_array[6],
                    'recipient': line_array[7]
                })

    def str_to_timestamp(time_string):
        date_time_obj = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
        return time.mktime(date_time_obj.timetuple())

    def calculate_simulation_duration(self):
        return self.raw_transactions[-1]['timestamp']-self.raw_transactions[0]['timestamp']

    def assign_accounts_to_shards(self):

    # def add_transaction_events_to_queue(self):
    #     Queue.add_event(Event(c.EVT_RECEIVE_TRANSACTION, node.id, event.time+0.5, event.data, event.id))
    #     pass
            



scheduler = Scheduler()
scheduler.load_transactions_from_file('static_data/data')


# print(scheduler.raw_transactions[100][0])
# print(scheduler.raw_transactions[100][1])
# print(scheduler.raw_transactions[100][2])
print(scheduler.calculate_simulation_duration())
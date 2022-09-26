from new_shard_sim.Topology import Topology
from new_shard_sim.Queue import Queue
from new_shard_sim.Event import Event
from new_shard_sim.Constants import *


class MetricsAggregator:
    def __init__(self):
        self.transaction_input_profile = {}
        self.transaction_output_profile = {}
        self.schedule_kickoff_events()

        # shard_id -> blockchain height that has been aggregated
        self.progress_map = self.initialize_progress_map()

    def get_amount_input_transactionsin_time_delta(self, current_time, time_delta):
        amount_input_transactions = 0

        for shard in Topology.shard_map.values():

            if shard.transaction_pool:

                transactions_in_range = [
                    transaction
                    for transaction in shard.transaction_pool
                    if transaction.timestamp >= current_time and transaction.timestamp < current_time + time_delta
                ]
                amount_input_transactions += len(transactions_in_range)

        self.transaction_input_profile[current_time] = amount_input_transactions

    def get_amount_output_transactions_in_time_delta(self, current_time):
        amount_output_transactions = 0

        blocks_under_analysis = Topology.root_shard.get_latest_blocks(self.progress_map[Topology.root_shard.id])
        self.progress_map[Topology.root_shard.id] = Topology.root_shard.get_current_blockchain_height()

        for block in blocks_under_analysis:
            amount_output_transactions += len(block.transactions)

            for child_block in block.child_blocks:
                child_shard = Topology.shard_map[child_block.shard_id]
                child_blocks_under_analysis = child_shard.get_blocks_within_height_range(
                    self.progress_map[child_shard.id], child_block.height
                )
                self.progress_map[child_shard.id] = child_block.height
                for block_in_range in child_blocks_under_analysis:
                    amount_output_transactions += len(block_in_range.transactions)

        self.transaction_output_profile[current_time] = amount_output_transactions

    def schedule_kickoff_events(self):
        Queue.add_event(
            Event(
                EVT_METRICS_AGGREGATE,
                0,
                0,
                "",
                HANDLER_METRICS_AGGREGATE,
            )
        )

        Queue.add_event(Event(EVT_METRICS_AGGREGATE_OUTPUT, 0, 0, "", HANDLER_METRICS_AGGREGATE_OUTPUT))

    def dump_metrics(self, file_name):
        with open(f"input_{file_name}.csv", "a") as file:
            for time, metric in self.transaction_input_profile.items():
                file.write(f"{time},{metric}\n")
        with open(f"output_{file_name}.csv", "a") as file:
            for time, metric in self.transaction_output_profile.items():
                file.write(f"{time},{metric}\n")

    def schedule_new_event(self, event, event_type, event_handler):
        Queue.add_event(Event(event_type, "", event.time + CST_METRICS_SAMPLING_PERIOD, "", event_handler))

    def initialize_progress_map(self):
        progress_map = {}
        for shard_id in Topology.shard_map.keys():
            progress_map[shard_id] = 1

        return progress_map

import os
from datetime import datetime
import json

from numpy import average

from new_shard_sim.Topology import Topology
from new_shard_sim.Queue import Queue
from new_shard_sim.Event import Event
from new_shard_sim.Logger import Logger
from new_shard_sim.Constants import *


class MetricsAggregator:
    def __init__(self, path):
        self.transaction_input_profile = {}
        self.transaction_output_profile = {}
        self.transaction_latency_profile = {}
        self.init_profiles()
        self.schedule_kickoff_events()
        self.path = path
        self.last_block_timestamp = 0

        # shard_id -> blockchain height that has been aggregated
        self.progress_map = self.initialize_progress_map()

    def init_profiles(self):
        self.transaction_input_profile["cross_shard_transactions"] = {}
        self.transaction_output_profile["cross_shard_transactions"] = {}

        for shard_id in Topology.shard_map.keys():
            self.transaction_input_profile[str(shard_id)] = {}
            self.transaction_output_profile[str(shard_id)] = {}
            self.transaction_latency_profile[str(shard_id)] = {}

    def get_amount_input_transactionsin_time_delta(self, current_time, time_delta):

        for shard in Topology.shard_map.values():
            amount_input_transactions = 0
            if shard.transaction_pool:

                transactions_in_range = [
                    transaction
                    for transaction in shard.transaction_pool
                    if transaction.timestamp >= current_time and transaction.timestamp < current_time + time_delta
                ]

                amount_input_transactions = len(transactions_in_range)

            if shard.children:
                if current_time in self.transaction_input_profile["cross_shard_transactions"]:
                    self.transaction_input_profile["cross_shard_transactions"][
                        current_time
                    ] += amount_input_transactions
                else:
                    self.transaction_input_profile["cross_shard_transactions"][current_time] = amount_input_transactions
            else:
                if current_time in self.transaction_input_profile[str(shard.id)]:
                    self.transaction_input_profile[str(shard.id)][current_time] += amount_input_transactions
                else:
                    self.transaction_input_profile[str(shard.id)][current_time] = amount_input_transactions

    def get_amount_output_transactions_in_time_delta(self, current_time):
        amount_output_transactions = 0

        blocks_under_analysis = Topology.root_shard.get_latest_blocks(self.progress_map[Topology.root_shard.id])
        self.progress_map[Topology.root_shard.id] = Topology.root_shard.get_current_blockchain_height()

        for block in blocks_under_analysis:
            amount_output_transactions += len(block.transactions)

            for child_block in block.child_blocks:
                child_shard = Topology.shard_map[str(child_block.shard_id)]
                child_blocks_under_analysis = child_shard.get_blocks_within_height_range(
                    self.progress_map[child_shard.id], child_block.height
                )
                self.progress_map[child_shard.id] = child_block.height
                for block_in_range in child_blocks_under_analysis:
                    amount_output_transactions += len(block_in_range.transactions)

        self.transaction_output_profile[current_time] = amount_output_transactions

    def get_amount_output_transactions_in_time_delta_with_stack(self, current_time):
        child_committed_block_index = {}
        search_stack = [Topology.root_shard]
        total_transactions_in_search = 0

        for record in self.transaction_output_profile.keys():
            self.transaction_output_profile[record][current_time] = 0

        while search_stack != []:
            current_shard = search_stack.pop()

            if current_shard.id == Topology.root_shard.id:
                latest_blocks = current_shard.blockchain.get_latest_blocks(self.progress_map[str(current_shard.id)])
            else:

                if (
                    current_shard.id in child_committed_block_index
                    and self.progress_map[current_shard.id] != child_committed_block_index[current_shard.id]
                ):
                    latest_blocks = current_shard.blockchain.get_blocks_within_height_range(
                        self.progress_map[current_shard.id], child_committed_block_index[current_shard.id]
                    )

                else:
                    continue

            if latest_blocks:
                self.progress_map[current_shard.id] = latest_blocks[-1].height

            amount_output_transactions = 0
            for block in latest_blocks:
                amount_output_transactions += len(block.transactions)

                if block.transactions:
                    if block.timestamp > self.last_block_timestamp:
                        self.last_block_timestamp = block.timestamp

                for transaction in block.transactions:
                    latency = current_time - transaction.timestamp
                    self.transaction_latency_profile[current_shard.id][transaction.id] = latency

                if block.child_blocks:
                    for child_block in block.child_blocks:
                        child_committed_block_index[child_block.shard_id] = child_block.height

            if current_shard.children:
                search_stack += current_shard.children

            if current_shard.children:
                self.transaction_output_profile["cross_shard_transactions"][current_time] += amount_output_transactions
            else:
                self.transaction_output_profile[str(current_shard.id)][current_time] += amount_output_transactions

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

        with open(f"{self.path}/raw_profiles.txt", "a") as file:
            file.write(f"{json.dumps(self.transaction_input_profile)} \n")
            file.write(f"{json.dumps(self.transaction_output_profile)} \n")
            file.write(f"{json.dumps(self.transaction_latency_profile)} \n")

            file.close()

        with open(f"{self.path}/input_cross_shard_transactions_{file_name}.csv", "a") as file:
            for time, metric in self.transaction_input_profile["cross_shard_transactions"].items():
                file.write(f"{time},{metric}\n")

            file.close()

        for shard in Topology.shard_leaf_map.values():
            if self.transaction_input_profile[str(shard.id)]:
                with open(
                    f"{self.path}/input_{shard.name}_{shard.id}_intra_shard_transactions_{file_name}.csv", "a"
                ) as file:
                    for time, metric in self.transaction_input_profile[str(shard.id)].items():
                        file.write(f"{time},{metric}\n")

                    file.close()

        with open(f"{self.path}/output_cross_shard_transactions_{file_name}.csv", "a") as file:
            for time, metric in self.transaction_output_profile["cross_shard_transactions"].items():
                file.write(f"{time},{metric}\n")

            file.close()

        for shard in Topology.shard_leaf_map.values():
            if self.transaction_output_profile[shard.id]:
                with open(
                    f"{self.path}/output_{shard.name}_{shard.id}_intra_shard_transactions_{file_name}.csv", "a"
                ) as file:
                    for time, metric in self.transaction_output_profile[shard.id].items():
                        file.write(f"{time},{metric}\n")

                    file.close()

        # latency

        for shard in Topology.shard_map.values():
            if self.transaction_latency_profile[shard.id]:
                with open(
                    f"{self.path}/{shard.name}_{shard.id}_shard_transactions_latency_{file_name}.csv", "a"
                ) as file:
                    for transaction_id, latency in self.transaction_latency_profile[shard.id].items():
                        file.write(f"{transaction_id},{latency}\n")

                    file.close()

        with open(f"{self.path}/topology.txt", "a") as file:
            file.write(Topology.print_class())
            file.close()

    def report(self, file_name):
        # average intra_shard_latency
        amount_transactions = 0
        intra_shard_latency_accum = 0
        for shard_id in Topology.shard_leaf_map.keys():
            for transaction_latency in self.transaction_latency_profile[shard_id].values():
                intra_shard_latency_accum += transaction_latency
                amount_transactions += 1

        average_intra_shard_latency = intra_shard_latency_accum / amount_transactions

        # average intra_shard_throughput

        # partial_average_intrashard_throughput = 0
        # for shard_id in Topology.shard_leaf_map.keys():

        #     metric_accum = 0
        #     intra_shard_accum = 0
        #     amount_samples = 0
        #     for time, metric in self.transaction_output_profile[shard_id].items():
        #         metric_accum += metric

        #         if time > self.last_block_timestamp:
        #             break

        #         if time % REPORT_METRICS_PERIOD == 0:
        #             amount_samples += 1
        #             intra_shard_accum = metric_accum
        #             metric_accum = 0

        #     partial_average_intrashard_throughput += intra_shard_accum / amount_samples

        most_active_shard_id = None
        most_active_shard_transaction_amount = 0
        for shard_id in Topology.shard_leaf_map.keys():

            metric_accum = 0
            for time, metric in self.transaction_output_profile[shard_id].items():
                metric_accum += metric

                if time > self.last_block_timestamp:
                    break

            if metric_accum > most_active_shard_transaction_amount:
                most_active_shard_transaction_amount = metric_accum
                most_active_shard_id = shard_id

        amount_samples = 0
        for time in self.transaction_output_profile[most_active_shard_id].keys():
            if time > self.last_block_timestamp:
                break
            if time % REPORT_METRICS_PERIOD == 0:
                amount_samples += 1

        average_intrashard_throughput = most_active_shard_transaction_amount / amount_samples

        # cross_shard_latency
        # lets get an average of root shard
        # Topology.root_shard.id
        # self.transaction_latency_profile

        average_cross_shard_latency = sum(
            [
                transaction_latency
                for transaction_latency in self.transaction_latency_profile[Topology.root_shard.id].values()
            ]
        ) / len(self.transaction_latency_profile[Topology.root_shard.id].values())

        # cross_shard_throughgput
        metric_accum = 0
        amount_samples = 0
        for time, metric in self.transaction_output_profile["cross_shard_transactions"].items():
            metric_accum += metric

            if time > self.last_block_timestamp:
                break

            if time % REPORT_METRICS_PERIOD == 0:
                amount_samples += 1

        average_cross_shard_throughput = metric_accum / amount_samples

        report = f"{average_intrashard_throughput},{average_intra_shard_latency},{average_cross_shard_throughput},{average_cross_shard_latency}"

        with open(f"{self.path}/{file_name}.csv", "a") as file:
            file.write(report)
            file.close()

    def schedule_new_event(self, event, event_type, event_handler):
        Queue.add_event(Event(event_type, "", event.time + CST_METRICS_SAMPLING_PERIOD, "", event_handler))

    def initialize_progress_map(self):
        progress_map = {}
        for shard_id in Topology.shard_map.keys():
            progress_map[shard_id] = 1

        return progress_map

from new_shard_sim.Topology import Topology
from new_shard_sim.Engine import Engine
from new_shard_sim.Event import Event
from new_shard_sim.Constants import *
from new_shard_sim.MetricsAggregator import MetricsAggregator


def block_create_handler(event: Event):
    shard = Topology.get_shard_from_id(event.shard_id)
    shard.create_block(event)


Engine.register_handler(HANDLER_CREATE_BLOCK, block_create_handler)


def transaction_receive_handler(event: Event):
    shard = Topology.get_shard_from_id(event.shard_id)
    shard.receive_transaction(event)


Engine.register_handler(HANDLER_RECEIVE_TRANSACTION, transaction_receive_handler)


def metrics_aggregate_handler(event: Event):
    Topology.metrics_aggregator.get_amount_input_transactionsin_time_delta(event.time, CST_METRICS_SAMPLING_PERIOD)
    Topology.metrics_aggregator.schedule_new_event(event, EVT_METRICS_AGGREGATE, HANDLER_METRICS_AGGREGATE)


Engine.register_handler(HANDLER_METRICS_AGGREGATE, metrics_aggregate_handler)


def metrics_aggregate_output_handler(event: Event):
    Topology.metrics_aggregator.get_amount_output_transactions_in_time_delta_with_stack(event.time)
    Topology.metrics_aggregator.schedule_new_event(
        event, EVT_METRICS_AGGREGATE_OUTPUT, HANDLER_METRICS_AGGREGATE_OUTPUT
    )


Engine.register_handler(HANDLER_METRICS_AGGREGATE_OUTPUT, metrics_aggregate_output_handler)

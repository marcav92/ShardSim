from distutils.debug import DEBUG


DEBUG = False
BLOCK_SIZE = 300
CHILD_BLOCKS_PER_BLOCK = 20
BLOCK_CREATION_INTERVAL = 10000

# modules
ENGINE = "engine"
METRICS_AGGREGATOR = "metrics_aggregator"

CST_MILISECONDS_IN_DAY = 86400 * 1000
CST_EXP_DELAY_LAMBDA = 10
CST_METRICS_SAMPLING_PERIOD = 1000

REPORT_METRICS_PERIOD = 1000

ARG_TRANSACTIONS_INPUT_FILE = "transactions_input_file"
ARG_SHARDS = "shards"
ARGS_METRICS_AGGREGATOR = "metrics_aggregator"
ARGS_ROOT_SHARD = "root_shard"
ARGS_COMPUTE_TRANSACTION_SUBGRAPHS = "compute_transaction_subgraphs"
ARGS_TXS_LABELS_FILE_PREFIX = "txs_label_file_prefix"
ARGS_TXS_GRAPH_NODES_FILE_NAME = "txs_graph_nodes_file_name"
ARGS_TXS_SPEC_LABELS_FILE_NAME = "txs_spec_labels_file_name"

HANDLER_CREATE_BLOCK = "handler_create_block"
HANDLER_RECEIVE_TRANSACTION = "handler_receive_block"
HANDLER_METRICS_AGGREGATE = "handler_metrics_aggregate"
HANDLER_METRICS_AGGREGATE_OUTPUT = "handler_metrics_aggregate_output"

EVT_CREATE_BLOCK = "evt_create_block"
EVT_TRANSACTION_RECEIVE = "evt_transaction_receive"
EVT_METRICS_AGGREGATE = "evt_metrics_aggregate"
EVT_METRICS_AGGREGATE_OUTPUT = "evt_metrics_aggregate_output"

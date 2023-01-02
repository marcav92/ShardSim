import os

result_summary = []

MINIMUM_AMOUNT_OF_RUNS = 5

AMOUNT_SHARDS_POSITION = 0
CHILDREN_PER_SHARD_POSITION = 1
AMOUNT_LEVELS_POSITION = 2
TRANSACTION_RATE_POSITION = 3

INTRASHARD_THROUGHPUT_POSITION = 4
INTRASHARD_LATENCY_POSITION = 5
CROSSSHARD_THROUGHPUT_POSITION = 6
CROSSSHARD_LATENCY_POSITION = 7

dir_list = os.listdir("./")


def dir_name_to_tuple(dir_name):
    dir_name_list = dir_name.split("-")
    shards = int(dir_name_list[1])
    children = int(dir_name_list[3])
    levels = int(dir_name_list[5])
    transaction_rate = int(dir_name_list[7])

    return (shards, children, levels, transaction_rate)


for dir in dir_list:
    if dir.startswith("run"):
        runs_dir_list = os.listdir(f"./{dir}")

        if len(runs_dir_list) < MINIMUM_AMOUNT_OF_RUNS:
            print(f"WARNING: there are nopt enough runs in {dir}")
            # this could trigger an exception in the future

        for index, run_dir in enumerate(runs_dir_list):
            run_file_list = os.listdir(f"./{dir}/{run_dir}")
            for run_file in run_file_list:
                if run_file.startswith("report"):
                    with open(f"./{dir}/{run_dir}/{run_file}", "r") as file:
                        lines = file.read()
                        result_tuple = tuple(lines.split(","))

                        floats = tuple([float(x) for x in result_tuple])

                        result_summary.append(dir_name_to_tuple(dir) + floats)

import numpy as np
import pandas as pd

# df_intra_throughput = pd.DataFrame(
#     {
#         "shards": [result[AMOUNT_SHARDS_POSITION] for result in result_summary],
#         "children": [result[CHILDREN_PER_SHARD_POSITION] for result in result_summary],
#         "levels": [result[AMOUNT_LEVELS_POSITION] for result in result_summary],
#         "transaction_rate": [result[TRANSACTION_RATE_POSITION] for result in result_summary],
#         "intrashard_throughput": [result[INTRASHARD_THROUGHPUT_POSITION] for result in result_summary],
#     }
# )

# df_intra_latency = pd.DataFrame(
#     {
#         "shards": np.array([result[AMOUNT_SHARDS_POSITION] for result in result_summary]),
#         "children": np.array([result[CHILDREN_PER_SHARD_POSITION] for result in result_summary]),
#         "levels": np.array([result[AMOUNT_LEVELS_POSITION] for result in result_summary]),
#         "transaction_rate": np.array([result[TRANSACTION_RATE_POSITION] for result in result_summary]),
#         "intrashard_latency": [result[INTRASHARD_LATENCY_POSITION] for result in result_summary],
#     }
# )

df_intra_latency = pd.DataFrame(
    {
        "shards": [10, 10, 10, 10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 15, 20, 20, 20, 20, 20, 25, 25, 25, 25, 25],
        "children": [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 5, 5, 5, 5],
        "levels": [3, 3, 3, 3, 2, 2, 2, 2, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1],
        "transaction_rate": [
            202,
            202,
            202,
            202,
            202,
            202,
            202,
            202,
            202,
            202,
            200,
            200,
            200,
            200,
            200,
            200,
            200,
            200,
            200,
            200,
            200,
            200,
            200,
            200,
        ],
        "intrashard_latency": [result[INTRASHARD_LATENCY_POSITION] for result in result_summary],
    }
)


# df_cross_throughput = pd.DataFrame(
#     {
#         "shards": [result[AMOUNT_SHARDS_POSITION] for result in result_summary],
#         "children": [result[CHILDREN_PER_SHARD_POSITION] for result in result_summary],
#         "levels": [result[AMOUNT_LEVELS_POSITION] for result in result_summary],
#         "transaction_rate": [result[TRANSACTION_RATE_POSITION] for result in result_summary],
#         "crossshard_throughput": [result[CROSSSHARD_THROUGHPUT_POSITION] for result in result_summary],
#     }
# )


# df_cross_latency = pd.DataFrame(
#     {
#         "shards": [result[AMOUNT_SHARDS_POSITION] for result in result_summary],
#         "children": [result[CHILDREN_PER_SHARD_POSITION] for result in result_summary],
#         "levels": [result[AMOUNT_LEVELS_POSITION] for result in result_summary],
#         "transaction_rate": [result[TRANSACTION_RATE_POSITION] for result in result_summary],
#         "crossshard_latency": [result[CROSSSHARD_LATENCY_POSITION] for result in result_summary],
#     }
# )

# print(df_intra_throughput)
print(df_intra_latency)
# print(df_cross_throughput)
# print(df_cross_latency)

import statsmodels.api as sm
from statsmodels.formula.api import ols

# model_intra_throughput = ols(
#     """intrashard_throughput ~ C(shards) + C(children) + C(levels) + C(transaction_rate) +
#                C(shards):C(children) + C(shards):C(levels) + C(shards):C(transaction_rate) +
#                C(children):C(levels) + C(children):C(transaction_rate) + C(levels):C(transaction_rate) +
#                C(shards):C(children):C(levels) + C(shards):C(children):C(transaction_rate) +
#                C(children):C(levels):C(transaction_rate) + C(shards):C(levels):C(transaction_rate) +
#                C(shards):C(children):C(levels):C(transaction_rate)""",
#     data=df_intra_throughput,
# ).fit()

# print(sm.stats.anova_lm(model_intra_throughput, typ=2))

model_intra_latency = ols(
    """intrashard_latency ~ C(shards) + C(children) + C(levels) + C(transaction_rate) +
               C(shards):C(children) + C(shards):C(levels) + C(shards):C(transaction_rate) +
               C(children):C(levels) + C(children):C(transaction_rate) + C(levels):C(transaction_rate) +
               C(shards):C(children):C(levels) + C(shards):C(children):C(transaction_rate) +
               C(children):C(levels):C(transaction_rate) + C(shards):C(levels):C(transaction_rate) +
               C(shards):C(children):C(levels):C(transaction_rate)""",
    data=df_intra_latency,
).fit()

print(sm.stats.anova_lm(model_intra_latency, typ=2))


# model_cross_throughput = ols(
#     """crossshard_throughput ~ C(shards) + C(children) + C(levels) + C(transaction_rate) +
#                C(shards):C(children) + C(shards):C(levels) + C(shards):C(transaction_rate) +
#                C(shards):C(children):C(levels):C(transaction_rate)""",
#     data=df_cross_throughput,
# ).fit()

# print(sm.stats.anova_lm(model_cross_throughput, typ=2))

# model_cross_latency = ols(
#     """crossshard_latency ~ C(shards) + C(children) + C(levels) + C(transaction_rate) +
#                C(shards):C(children) + C(shards):C(levels) + C(shards):C(transaction_rate) +
#                C(shards):C(children):C(levels):C(transaction_rate)""",
#     data=df_cross_latency,
# ).fit()

# print(sm.stats.anova_lm(model_cross_latency, typ=2))

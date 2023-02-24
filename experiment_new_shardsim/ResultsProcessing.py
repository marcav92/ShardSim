import os

result_summary = []

MINIMUM_AMOUNT_OF_RUNS = 5

AMOUNT_SHARDS_POSITION = 0
CHILDREN_PER_SHARD_POSITION = 1
AMOUNT_LEVELS_POSITION = 2
TRANSACTION_RATE_POSITION = 3
# TRANSACTION_FILE_POSITION = 4

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
    # transaction_file = dir_name_list[9]

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
import matplotlib.pyplot as plt

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D

df_intra_throughput = pd.DataFrame(
    {
        "shards": [result[AMOUNT_SHARDS_POSITION] for result in result_summary],
        "children": [result[CHILDREN_PER_SHARD_POSITION] for result in result_summary],
        "levels": [result[AMOUNT_LEVELS_POSITION] for result in result_summary],
        "transaction_rate": [result[TRANSACTION_RATE_POSITION] for result in result_summary],
        # "transaction_file": [result[TRANSACTION_FILE_POSITION] for result in result_summary],
        "intrashard_throughput": [result[INTRASHARD_THROUGHPUT_POSITION] for result in result_summary],
    }
)

# df_intra_throughput.plot(kind="line", x="shards", y="intrashard_throughput", color="red")
# df_intra_throughput.plot(kind="line", x="children", y="intrashard_throughput", color="red")
# df_intra_throughput.plot(kind="line", x="levels", y="intrashard_throughput", color="red")
# df_intra_throughput.plot(kind="line", x="transaction_rate", y="intrashard_throughput", color="red")

intra_throughput_3d_figure = plt.figure().gca(projection="3d")

intra_throughput_3d_figure.scatter(
    df_intra_throughput["children"],
    df_intra_throughput["shards"],
    df_intra_throughput["intrashard_throughput"],
)

intra_throughput_3d_figure.set_xlabel("children per shard")
intra_throughput_3d_figure.set_ylabel("shards")
intra_throughput_3d_figure.set_zlabel("intrashard_throughput")

# plt.show()

df_intra_latency = pd.DataFrame(
    {
        "shards": np.array([result[AMOUNT_SHARDS_POSITION] for result in result_summary]),
        "children": np.array([result[CHILDREN_PER_SHARD_POSITION] for result in result_summary]),
        "levels": np.array([result[AMOUNT_LEVELS_POSITION] for result in result_summary]),
        "transaction_rate": np.array([result[TRANSACTION_RATE_POSITION] for result in result_summary]),
        # "transaction_file": [result[TRANSACTION_FILE_POSITION] for result in result_summary],
        "intrashard_latency": [result[INTRASHARD_LATENCY_POSITION] for result in result_summary],
    }
)

# df_intra_latency.plot(kind="line", x="shards", y="intrashard_latency", color="red")
# df_intra_latency.plot(kind="line", x="children", y="intrashard_latency", color="red")
# df_intra_latency.plot(kind="line", x="levels", y="intrashard_latency", color="red")
# df_intra_latency.plot(kind="line", x="transaction_rate", y="intrashard_latency", color="red")

intra_latency_3d_figure = plt.figure().gca(projection="3d")

intra_latency_3d_figure.scatter(
    df_intra_latency["children"],
    df_intra_latency["shards"],
    df_intra_latency["intrashard_latency"],
)

intra_latency_3d_figure.set_xlabel("children per shard")
intra_latency_3d_figure.set_ylabel("shards")
intra_latency_3d_figure.set_zlabel("intrashard_latency")


df_cross_throughput = pd.DataFrame(
    {
        "shards": [result[AMOUNT_SHARDS_POSITION] for result in result_summary],
        "children": [result[CHILDREN_PER_SHARD_POSITION] for result in result_summary],
        "levels": [result[AMOUNT_LEVELS_POSITION] for result in result_summary],
        "transaction_rate": [result[TRANSACTION_RATE_POSITION] for result in result_summary],
        # "transaction_file": [result[TRANSACTION_FILE_POSITION] for result in result_summary],
        "crossshard_throughput": [result[CROSSSHARD_THROUGHPUT_POSITION] for result in result_summary],
    }
)

# df_cross_throughput.plot(kind="line", x="shards", y="crossshard_throughput", color="red")
# df_cross_throughput.plot(kind="line", x="children", y="crossshard_throughput", color="red")
# df_cross_throughput.plot(kind="line", x="levels", y="crossshard_throughput", color="red")
# df_cross_throughput.plot(kind="line", x="transaction_rate", y="crossshard_throughput", color="red")

cross_throughput_3d_figure = plt.figure().gca(projection="3d")

cross_throughput_3d_figure.scatter(
    df_cross_throughput["levels"],
    df_cross_throughput["shards"],
    df_cross_throughput["crossshard_throughput"],
)

cross_throughput_3d_figure.set_xlabel("levels")
cross_throughput_3d_figure.set_ylabel("shards")
cross_throughput_3d_figure.set_zlabel("crossshard_throughput")


# plt.show()

df_cross_latency = pd.DataFrame(
    {
        "shards": [result[AMOUNT_SHARDS_POSITION] for result in result_summary],
        "children": [result[CHILDREN_PER_SHARD_POSITION] for result in result_summary],
        "levels": [result[AMOUNT_LEVELS_POSITION] for result in result_summary],
        "transaction_rate": [result[TRANSACTION_RATE_POSITION] for result in result_summary],
        # "transaction_file": [result[TRANSACTION_FILE_POSITION] for result in result_summary],
        "crossshard_latency": [result[CROSSSHARD_LATENCY_POSITION] for result in result_summary],
    }
)

cross_latency_3d_figure = plt.figure().gca(projection="3d")

cross_latency_3d_figure.scatter(
    df_cross_latency["children"],
    df_cross_latency["shards"],
    df_cross_latency["crossshard_latency"],
)

cross_latency_3d_figure.set_xlabel("children per shard")
cross_latency_3d_figure.set_ylabel("shards")
cross_latency_3d_figure.set_zlabel("crossshard_latency")

plt.show()

print(df_intra_throughput)
print(df_intra_latency)
print(df_cross_throughput)
print(df_cross_latency)

import statsmodels.api as sm
from statsmodels.formula.api import ols

model_intra_throughput = ols(
    """intrashard_throughput ~ C(shards) + C(children) + C(levels) + C(transaction_rate) +
               C(shards):C(children) + C(shards):C(levels) + C(shards):C(transaction_rate) +
               C(children):C(levels) + C(children):C(transaction_rate) + C(levels):C(transaction_rate) +
               C(shards):C(children):C(levels) + C(shards):C(children):C(transaction_rate) +
               C(children):C(levels):C(transaction_rate) + C(shards):C(levels):C(transaction_rate) +
               C(shards):C(children):C(levels):C(transaction_rate)""",
    data=df_intra_throughput,
).fit()

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

# print(sm.stats.anova_lm(model_intra_latency, typ=2))


model_cross_throughput = ols(
    """crossshard_throughput ~ C(shards) + C(children) + C(levels) + C(transaction_rate) +
               C(shards):C(children) + C(shards):C(levels) + C(shards):C(transaction_rate) +
               C(children):C(levels) + C(children):C(transaction_rate) + C(levels):C(transaction_rate) +
               C(shards):C(children):C(levels) + C(shards):C(children):C(transaction_rate) +
               C(children):C(levels):C(transaction_rate) + C(shards):C(levels):C(transaction_rate) +
               C(shards):C(children):C(levels):C(transaction_rate)""",
    data=df_cross_throughput,
).fit()

# print(sm.stats.anova_lm(model_cross_throughput, typ=2))

model_cross_latency = ols(
    """crossshard_latency ~ C(shards) + C(children) + C(levels) + C(transaction_rate) +
               C(shards):C(children) + C(shards):C(levels) + C(shards):C(transaction_rate) +
               C(children):C(levels) + C(children):C(transaction_rate) + C(levels):C(transaction_rate) +
               C(shards):C(children):C(levels) + C(shards):C(children):C(transaction_rate) +
               C(children):C(levels):C(transaction_rate) + C(shards):C(levels):C(transaction_rate) +
               C(shards):C(children):C(levels):C(transaction_rate)""",
    data=df_cross_latency,
).fit()

# print(sm.stats.anova_lm(model_cross_latency, typ=2))

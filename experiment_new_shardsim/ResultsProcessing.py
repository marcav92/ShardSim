import os

result_summary = []

MINIMUM_AMOUNT_OF_RUNS = 5

AMOUNT_SHARDS_POSITION = 0
CHILDREN_PER_SHARD_POSITION = 1
AMOUNT_LEVELS_POSITION = 2
CROSS_SHARD_TRANSACTION_RATIO = 3
TRANSACTION_RATE_POSITION = 4
# TRANSACTION_FILE_POSITION = 4

INTRASHARD_THROUGHPUT_POSITION = 5
INTRASHARD_LATENCY_POSITION = 6
CROSSSHARD_THROUGHPUT_POSITION = 7
CROSSSHARD_LATENCY_POSITION = 8

dir_list = os.listdir("./")


def dir_name_to_tuple(dir_name):
    dir_name_list = dir_name.split("-")
    shards = int(dir_name_list[1])
    children = int(dir_name_list[3])
    levels = int(dir_name_list[5])
    cross_shard_transaction_ratio = float(dir_name_list[7])
    transaction_rate = int(dir_name_list[8])
    # transaction_file = dir_name_list[9]

    return (shards, children, levels, cross_shard_transaction_ratio, transaction_rate)

def add_number_labels_bar_plot(ax):
    for container in ax.containers:
        for bar in container:
            ax.text(
                bar.get_x() + bar.get_width() / 2,  # X-coordinate of the label
                # 0.5,
                bar.get_height() / 2,  # Y-coordinate of the label
                round(bar.get_height(), 1),  # Text value (height of the bar)
                ha='center',  # Horizontal alignment
                va='bottom',  # Vertical alignment
            )

for dir in dir_list:
    # print("this is dir: ", dir)
    if dir.startswith("run"):
        runs_dir_list = os.listdir(f"./{dir}")
        # print("this is run_dir_list: ", runs_dir_list)

        if len(runs_dir_list) < MINIMUM_AMOUNT_OF_RUNS:
            print(f"WARNING: there are nopt enough runs in {dir}")
            # this could trigger an exception in the future

        for index, run_dir in enumerate(runs_dir_list):
            if run_dir == ".DS_Store":
                continue
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
        "cross_shard_transaction_ratio": [result[CROSS_SHARD_TRANSACTION_RATIO] for result in result_summary],
        "transaction_rate": [result[TRANSACTION_RATE_POSITION] for result in result_summary],
        "intrashard_throughput": [result[INTRASHARD_THROUGHPUT_POSITION] for result in result_summary],
    }
)

df_intra_throughput = df_intra_throughput.drop_duplicates(subset=["shards", "children", "levels", "cross_shard_transaction_ratio", "transaction_rate", "intrashard_throughput"])

df_intra_throughput_filtered = df_intra_throughput[
    df_intra_throughput["shards"] == 10
]

# print(df_intra_throughput_filtered)

df_filtered_5_shards = df_intra_throughput[
    (df_intra_throughput["shards"] == 5) &
    (df_intra_throughput["transaction_rate"] == 200) &
    (df_intra_throughput["cross_shard_transaction_ratio"] == 0.10)
]

df_filtered_5_shards = df_filtered_5_shards.sort_values('levels')

df_filtered_5_shards_average = df_filtered_5_shards.groupby('levels').mean()

df_filtered_10_shards = df_intra_throughput[
    (df_intra_throughput["shards"] == 10) &
    (df_intra_throughput["transaction_rate"] == 200) &
    (df_intra_throughput["cross_shard_transaction_ratio"] == 0.10)
]

df_filtered_10_shards = df_filtered_10_shards.sort_values('levels')

df_filtered_10_shards_average = df_filtered_10_shards.groupby('levels').mean()

df_filtered_20_shards = df_intra_throughput[
    (df_intra_throughput["shards"] == 20) &
    (df_intra_throughput["transaction_rate"] == 200) &
    (df_intra_throughput["cross_shard_transaction_ratio"] == 0.10)
]

df_filtered_20_shards = df_filtered_20_shards.sort_values('levels')

df_filtered_20_shards_average = df_filtered_20_shards.groupby('levels').mean()

df_filtered_30_shards = df_intra_throughput[
    (df_intra_throughput["shards"] == 30) &
    (df_intra_throughput["transaction_rate"] == 200) &
    (df_intra_throughput["cross_shard_transaction_ratio"] == 0.10)
]

df_filtered_30_shards = df_filtered_30_shards.sort_values('levels')

df_filtered_30_shards_average = df_filtered_30_shards.groupby('levels').mean()

df_filtered_50_shards = df_intra_throughput[
    (df_intra_throughput["shards"] == 50) &
    (df_intra_throughput["transaction_rate"] == 200) &
    (df_intra_throughput["cross_shard_transaction_ratio"] == 0.10)
]

df_filtered_50_shards = df_filtered_50_shards.sort_values('levels')

df_filtered_50_shards_average = df_filtered_50_shards.groupby('levels').mean()

fig, ax = plt.subplots(nrows=2, ncols=3)

ax_5  =  df_filtered_5_shards_average.plot.bar(y="intrashard_throughput", width=0.5, rot=0, ax=ax[0,0],  color="green", alpha=0.5, legend=False)
ax_10 = df_filtered_10_shards_average.plot.bar(y="intrashard_throughput", width=0.5, rot=0, ax=ax[0,1], color="green", alpha=0.5, legend=False)
ax_20 = df_filtered_20_shards_average.plot.bar(y="intrashard_throughput", width=0.5, rot=0, ax=ax[0,2], color="green", alpha=0.5, legend=False)
ax_30 = df_filtered_30_shards_average.plot.bar(y="intrashard_throughput", width=0.5, rot=0, ax=ax[1,0], color="green", alpha=0.5, legend=False)
ax_50 = df_filtered_50_shards_average.plot.bar(y="intrashard_throughput", width=0.5, rot=0, ax=ax[1,1], color="green", alpha=0.5, legend=False)


add_number_labels_bar_plot(ax_5)
add_number_labels_bar_plot(ax_10)
add_number_labels_bar_plot(ax_20)
add_number_labels_bar_plot(ax_30)
add_number_labels_bar_plot(ax_50)


ax[0,0].set_xlabel('Hierarchy levels')
ax[0,0].set_ylabel('Intra Shard Throughput (Tx/s)')
ax[0,0].set_title('5 Shards')

ax[0,1].set_xlabel('Hierarchy levels')
ax[0,1].set_ylabel('Intra Shard Throughput (Tx/s)')
ax[0,1].set_title('10 Shards')

ax[0,2].set_xlabel('Hierarchy levels')
ax[0,2].set_ylabel('Intra Shard Throughput (Tx/s)')
ax[0,2].set_title('20 Shards')

ax[1,0].set_xlabel('Hierarchy levels')
ax[1,0].set_ylabel('Intra Shard Throughput (Tx/s)')
ax[1,0].set_title('30 Shards')

ax[1,1].set_xlabel('Hierarchy levels')
ax[1,1].set_ylabel('Intra Shard Throughput (Tx/s)')
ax[1,1].set_title('50 Shards')

# ax.set_title('Sales and Profits by Year')

ax[1,2].set_visible(False)

fig.tight_layout()

plt.show()

# df_intra_throughput = df_intra_throughput.loc[
#     (df_intra_throughput["shards"] == 30) &
#     (df_intra_throughput["cross_shard_transaction_ratio"] == 0.25) &
#     # (df_intra_throughput["levels"] == 3) &
#     (df_intra_throughput["transaction_rate"] == 200)
# ]

# average_intra_throughput = df_intra_throughput.groupby("cross_shard_transaction_ratio")["intrashard_throughput"].mean()
# print(average_intra_throughput)

# df_intra_throughput.plot(kind="line", x="shards", y="intrashard_throughput", color="red")
# df_intra_throughput.plot(kind="line", x="children", y="intrashard_throughput", color="red")
# df_intra_throughput.plot(kind="line", x="levels", y="intrashard_throughput", color="red")
# df_intra_throughput.plot(kind="line", x="transaction_rate", y="intrashard_throughput", color="red")
# df_intra_throughput.plot(kind="scatter", x="children", y="intrashard_throughput", color="red")


# intra_throughput_3d_figure = plt.figure().gca(projection="3d")

# intra_throughput_3d_figure = plt.figure()
# ax = intra_throughput_3d_figure.add_subplot(111, projection='3d')

# ax.scatter(
#     df_intra_throughput["shards"],
#     df_intra_throughput["levels"],
#     df_intra_throughput["intrashard_throughput"],
# )

# ax.set_xlabel("shards")
# ax.set_ylabel("levels")
# ax.set_zlabel("intrashard_throughput")

# plt.show()

df_intra_latency = pd.DataFrame(
    {
        "shards": np.array([result[AMOUNT_SHARDS_POSITION] for result in result_summary]),
        "children": np.array([result[CHILDREN_PER_SHARD_POSITION] for result in result_summary]),
        "levels": np.array([result[AMOUNT_LEVELS_POSITION] for result in result_summary]),
        "cross_shard_transaction_ratio": [result[CROSS_SHARD_TRANSACTION_RATIO] for result in result_summary],
        "transaction_rate": np.array([result[TRANSACTION_RATE_POSITION] for result in result_summary]),
        "intrashard_latency": [result[INTRASHARD_LATENCY_POSITION] for result in result_summary],
    }
)

df_intra_latency = df_intra_latency.drop_duplicates(subset=["shards", "children", "levels", "cross_shard_transaction_ratio", "transaction_rate", "intrashard_latency"])

df_intra_latency["intrashard_latency"] = df_intra_latency["intrashard_latency"] / 1000

df_intra_latency_filtered = df_intra_latency[
    df_intra_latency["shards"] == 10
]

# print(df_intra_latency)

df_intra_latency_filtered_5_shards = df_intra_latency[
    (df_intra_latency["shards"] == 5) &
    (df_intra_latency["transaction_rate"] == 200) &
    (df_intra_latency["cross_shard_transaction_ratio"] == 0.10)
]

df_intra_latency_filtered_5_shards = df_intra_latency_filtered_5_shards.sort_values('levels')

df_intra_latency_filtered_5_shards_average = df_intra_latency_filtered_5_shards.groupby('levels').mean()

df_intra_latency_filtered_10_shards = df_intra_latency[
    (df_intra_latency["shards"] == 10) &
    (df_intra_latency["transaction_rate"] == 200) &
    (df_intra_latency["cross_shard_transaction_ratio"] == 0.10)
]

df_intra_latency_filtered_10_shards = df_intra_latency_filtered_10_shards.sort_values('levels')

df_intra_latency_filtered_10_shards_average = df_intra_latency_filtered_10_shards.groupby('levels').mean()

df_intra_latency_filtered_20_shards = df_intra_latency[
    (df_intra_latency["shards"] == 20) &
    (df_intra_latency["transaction_rate"] == 200) &
    (df_intra_latency["cross_shard_transaction_ratio"] == 0.10)
]

df_intra_latency_filtered_20_shards = df_intra_latency_filtered_20_shards.sort_values('levels')

df_intra_latency_filtered_20_shards_average = df_intra_latency_filtered_20_shards.groupby('levels').mean()

df_intra_latency_filtered_30_shards = df_intra_latency[
    (df_intra_latency["shards"] == 30) &
    (df_intra_latency["transaction_rate"] == 200) &
    (df_intra_latency["cross_shard_transaction_ratio"] == 0.10)
]

df_intra_latency_filtered_30_shards = df_intra_latency_filtered_30_shards.sort_values('levels')

df_intra_latency_filtered_30_shards_average = df_intra_latency_filtered_30_shards.groupby('levels').mean()

df_intra_latency_filtered_50_shards = df_intra_latency[
    (df_intra_latency["shards"] == 50) &
    (df_intra_latency["transaction_rate"] == 200) &
    (df_intra_latency["cross_shard_transaction_ratio"] == 0.10)
]

df_intra_latency_filtered_50_shards = df_intra_latency_filtered_50_shards.sort_values('levels')

df_intra_latency_filtered_50_shards_average = df_intra_latency_filtered_50_shards.groupby('levels').mean()

fig_intra_latency, ax_intra_latency = plt.subplots(nrows=2, ncols=3)

ax_intra_latency_5  =  df_intra_latency_filtered_5_shards_average.plot.bar(y="intrashard_latency", label="5 Shards", width=0.5, rot=0, ax=ax_intra_latency[0,0], color="green", alpha=0.7, legend=False)
ax_intra_latency_10 = df_intra_latency_filtered_10_shards_average.plot.bar(y="intrashard_latency", label="10 Shards", width=0.5, rot=0, ax=ax_intra_latency[0,1], color="green", alpha=0.7, legend=False)
ax_intra_latency_20 = df_intra_latency_filtered_20_shards_average.plot.bar(y="intrashard_latency", label="20 Shards", width=0.5, rot=0, ax=ax_intra_latency[0,2], color="green", alpha=0.7, legend=False)
ax_intra_latency_30 = df_intra_latency_filtered_30_shards_average.plot.bar(y="intrashard_latency", label="30 Shards", width=0.5, rot=0, ax=ax_intra_latency[1,0], color="green", alpha=0.7, legend=False)
ax_intra_latency_50 = df_intra_latency_filtered_50_shards_average.plot.bar(y="intrashard_latency", label="50 Shards", width=0.5, rot=0, ax=ax_intra_latency[1,1], color="green", alpha=0.7, legend=False)

add_number_labels_bar_plot(ax_intra_latency_5)
add_number_labels_bar_plot(ax_intra_latency_10)
add_number_labels_bar_plot(ax_intra_latency_20)
add_number_labels_bar_plot(ax_intra_latency_30)
add_number_labels_bar_plot(ax_intra_latency_50)

ax_intra_latency[0,0].set_xlabel('Hierarchy levels')
ax_intra_latency[0,0].set_ylabel('Intra Shard Latency (s)')
ax_intra_latency[0,0].set_title('5 Shards')
ax_intra_latency[0,1].set_xlabel('Hierarchy levels')
ax_intra_latency[0,1].set_ylabel('Intra Shard Latency (s)')
ax_intra_latency[0,1].set_title('10 Shards')
ax_intra_latency[0,2].set_xlabel('Hierarchy levels')
ax_intra_latency[0,2].set_ylabel('Intra Shard Latency (s)')
ax_intra_latency[0,2].set_title('20 Shards')
ax_intra_latency[1,0].set_xlabel('Hierarchy levels')
ax_intra_latency[1,0].set_ylabel('Intra Shard Latency (s)')
ax_intra_latency[1,0].set_title('30 Shards')
ax_intra_latency[1,1].set_xlabel('Hierarchy levels')
ax_intra_latency[1,1].set_ylabel('Intra Shard Latency (s)')
ax_intra_latency[1,1].set_title('50 Shards')

ax_intra_latency[1,2].set_visible(False)

fig_intra_latency.tight_layout()

plt.show()

# df_intra_latency.plot(kind="line", x="shards", y="intrashard_latency", color="red")
# df_intra_latency.plot(kind="line", x="children", y="intrashard_latency", color="red")
# df_intra_latency.plot(kind="line", x="levels", y="intrashard_latency", color="red")
# df_intra_latency.plot(kind="line", x="cross_shard_transaction_ratio", y="intrashard_latency", color="red")

# intra_latency_3d_figure = plt.figure().gca(projection="3d")

# intra_latency_3d_figure.scatter(
#     df_intra_latency["children"],
#     df_intra_latency["shards"],
#     df_intra_latency["intrashard_latency"],
# )

# intra_latency_3d_figure.set_xlabel("children per shard")
# intra_latency_3d_figure.set_ylabel("shards")
# intra_latency_3d_figure.set_zlabel("intrashard_latency")


df_cross_throughput = pd.DataFrame(
    {
        "shards": [result[AMOUNT_SHARDS_POSITION] for result in result_summary],
        "children": [result[CHILDREN_PER_SHARD_POSITION] for result in result_summary],
        "levels": [result[AMOUNT_LEVELS_POSITION] for result in result_summary],
        "cross_shard_transaction_ratio": [result[CROSS_SHARD_TRANSACTION_RATIO] for result in result_summary],
        "transaction_rate": [result[TRANSACTION_RATE_POSITION] for result in result_summary],
        "crossshard_throughput": [result[CROSSSHARD_THROUGHPUT_POSITION] for result in result_summary],
    }
)

df_cross_throughput = df_cross_throughput.drop_duplicates(subset=["shards", "children", "levels", "cross_shard_transaction_ratio", "transaction_rate", "crossshard_throughput"])

df_cross_throughput_filtered = df_cross_throughput[
    df_cross_throughput["shards"] == 10
]

# print(df_cross_throughput)

df_cross_throughput_filtered_5_shards = df_cross_throughput[
    (df_cross_throughput["shards"] == 5) &
    (df_cross_throughput["transaction_rate"] == 200) &
    (df_cross_throughput["cross_shard_transaction_ratio"] == 0.25)
]

df_cross_throughput_filtered_5_shards = df_cross_throughput_filtered_5_shards.sort_values('levels')

df_cross_throughput_filtered_5_shards_average = df_cross_throughput_filtered_5_shards.groupby('levels').mean()

df_cross_throughput_filtered_10_shards = df_cross_throughput[
    (df_cross_throughput["shards"] == 10) &
    (df_cross_throughput["transaction_rate"] == 200) &
    (df_cross_throughput["cross_shard_transaction_ratio"] == 0.25)
]

df_cross_throughput_filtered_10_shards = df_cross_throughput_filtered_10_shards.sort_values('levels')

df_cross_throughput_filtered_10_shards_average = df_cross_throughput_filtered_10_shards.groupby('levels').mean()

df_cross_throughput_filtered_20_shards = df_cross_throughput[
    (df_cross_throughput["shards"] == 20) &
    (df_cross_throughput["transaction_rate"] == 200) &
    (df_cross_throughput["cross_shard_transaction_ratio"] == 0.25)
]

df_cross_throughput_filtered_20_shards = df_cross_throughput_filtered_20_shards.sort_values('levels')

df_cross_throughput_filtered_20_shards_average = df_cross_throughput_filtered_20_shards.groupby('levels').mean()

df_cross_throughput_filtered_30_shards = df_cross_throughput[
    (df_cross_throughput["shards"] == 30) &
    (df_cross_throughput["transaction_rate"] == 200) &
    (df_cross_throughput["cross_shard_transaction_ratio"] == 0.25)
]

df_cross_throughput_filtered_30_shards = df_cross_throughput_filtered_30_shards.sort_values('levels')

df_cross_throughput_filtered_30_shards_average = df_cross_throughput_filtered_30_shards.groupby('levels').mean()

df_cross_throughput_filtered_50_shards = df_cross_throughput[
    (df_cross_throughput["shards"] == 50) &
    (df_cross_throughput["transaction_rate"] == 200) &
    (df_cross_throughput["cross_shard_transaction_ratio"] == 0.25)
]

df_cross_throughput_filtered_50_shards = df_cross_throughput_filtered_50_shards.sort_values('levels')

df_cross_throughput_filtered_50_shards_average = df_cross_throughput_filtered_50_shards.groupby('levels').mean()

fig_cross_throughput, ax_cross_throughput = plt.subplots(nrows=2, ncols=3)

ax_cross_throughput_5  =  df_cross_throughput_filtered_5_shards_average.plot.bar(y="crossshard_throughput", label="5 Shards", width=0.5, rot=0, ax=ax_cross_throughput[0,0], color="green", alpha=0.5, legend=False)
ax_cross_throughput_10 = df_cross_throughput_filtered_10_shards_average.plot.bar(y="crossshard_throughput", label="10 Shards", width=0.5, rot=0, ax=ax_cross_throughput[0,1], color="green", alpha=0.5, legend=False)
ax_cross_throughput_20 = df_cross_throughput_filtered_20_shards_average.plot.bar(y="crossshard_throughput", label="20 Shards", width=0.5, rot=0, ax=ax_cross_throughput[0,2], color="green", alpha=0.5, legend=False)
ax_cross_throughput_30 = df_cross_throughput_filtered_30_shards_average.plot.bar(y="crossshard_throughput", label="30 Shards", width=0.5, rot=0, ax=ax_cross_throughput[1,0], color="green", alpha=0.5, legend=False)
ax_cross_throughput_50 = df_cross_throughput_filtered_50_shards_average.plot.bar(y="crossshard_throughput", label="50 Shards", width=0.5, rot=0, ax=ax_cross_throughput[1,1], color="green", alpha=0.5, legend=False)

add_number_labels_bar_plot(ax_cross_throughput_5)
add_number_labels_bar_plot(ax_cross_throughput_10)
add_number_labels_bar_plot(ax_cross_throughput_20)
add_number_labels_bar_plot(ax_cross_throughput_30)
add_number_labels_bar_plot(ax_cross_throughput_50)

ax_cross_throughput[0,0].set_xlabel('Hierarchy levels')
ax_cross_throughput[0,0].set_ylabel('Cross Shard Throughput (Tx/s)')
ax_cross_throughput[0,0].set_title('5 Shards')
ax_cross_throughput[0,1].set_xlabel('Hierarchy levels')
ax_cross_throughput[0,1].set_ylabel('Cross Shard Throughput (Tx/s)')
ax_cross_throughput[0,1].set_title('10 Shards')
ax_cross_throughput[0,2].set_xlabel('Hierarchy levels')
ax_cross_throughput[0,2].set_ylabel('Cross Shard Throughput (Tx/s)')
ax_cross_throughput[0,2].set_title('20 Shards')
ax_cross_throughput[1,0].set_xlabel('Hierarchy levels')
ax_cross_throughput[1,0].set_ylabel('Cross Shard Throughput (Tx/s)')
ax_cross_throughput[1,0].set_title('30 Shards')
ax_cross_throughput[1,1].set_xlabel('Hierarchy levels')
ax_cross_throughput[1,1].set_ylabel('Cross Shard Throughput (Tx/s)')
ax_cross_throughput[1,1].set_title('50 Shards')

ax_cross_throughput[1,2].set_visible(False)

fig_cross_throughput.tight_layout()

plt.show()

# df_cross_throughput = df_cross_throughput.loc[
#     # (df_cross_throughput["shards"] == 30) &
#     (df_cross_throughput["cross_shard_transaction_ratio"] == 0.25) &
#     # (df_intra_throughput["levels"] == 3) &
#     (df_cross_throughput["transaction_rate"] == 200)
# ]

# df_cross_throughput.plot(kind="line", x="shards", y="crossshard_throughput", color="red")
# df_cross_throughput.plot(kind="line", x="children", y="crossshard_throughput", color="red")
# df_cross_throughput.plot(kind="line", x="levels", y="crossshard_throughput", color="red")
# df_cross_throughput.plot(kind="scatter", x="cross_shard_transaction_ratio", y="crossshard_throughput", color="red")

# cross_throughput_3d_figure = plt.figure()
# axo = cross_throughput_3d_figure.add_subplot(111, projection='3d')

# axo.scatter(
#     df_cross_throughput["shards"],
#     df_cross_throughput["children"],
#     df_cross_throughput["crossshard_throughput"],
# )

# axo.set_xlabel("shards")
# axo.set_ylabel("children")
# axo.set_zlabel("crossshard_throughput")

# cross_throughput_3d_figure = plt.figure().gca(projection="3d")

# cross_throughput_3d_figure.scatter(
#     df_cross_throughput["levels"],
#     df_cross_throughput["shards"],
#     df_cross_throughput["crossshard_throughput"],
# )

# cross_throughput_3d_figure.set_xlabel("levels")
# cross_throughput_3d_figure.set_ylabel("shards")
# cross_throughput_3d_figure.set_zlabel("crossshard_throughput")


# plt.show()

df_cross_latency = pd.DataFrame(
    {
        "shards": [result[AMOUNT_SHARDS_POSITION] for result in result_summary],
        "children": [result[CHILDREN_PER_SHARD_POSITION] for result in result_summary],
        "levels": [result[AMOUNT_LEVELS_POSITION] for result in result_summary],
        "cross_shard_transaction_ratio": [result[CROSS_SHARD_TRANSACTION_RATIO] for result in result_summary],
        "transaction_rate": [result[TRANSACTION_RATE_POSITION] for result in result_summary],
        "crossshard_latency": [result[CROSSSHARD_LATENCY_POSITION] for result in result_summary],
    }
)

df_cross_latency = df_cross_latency.drop_duplicates(subset=["shards", "children", "levels", "cross_shard_transaction_ratio", "transaction_rate", "crossshard_latency"])

df_cross_latency["crossshard_latency"] = df_cross_latency["crossshard_latency"] / 1000

df_cross_latency_filtered = df_cross_latency[
    df_cross_latency["shards"] == 10
]

# print(df_cross_latency)

df_cross_latency_filtered_5_shards = df_cross_latency[
    (df_cross_latency["shards"] == 5) &
    (df_cross_latency["transaction_rate"] == 200) &
    (df_cross_latency["cross_shard_transaction_ratio"] == 0.25)
]

df_cross_latency_filtered_5_shards = df_cross_latency_filtered_5_shards.sort_values('levels')

df_cross_latency_filtered_5_shards_average = df_cross_latency_filtered_5_shards.groupby('levels').mean()

df_cross_latency_filtered_10_shards = df_cross_latency[
    (df_cross_latency["shards"] == 10) &
    (df_cross_latency["transaction_rate"] == 200) &
    (df_cross_latency["cross_shard_transaction_ratio"] == 0.25)
]

df_cross_latency_filtered_10_shards = df_cross_latency_filtered_10_shards.sort_values('levels')

df_cross_latency_filtered_10_shards_average = df_cross_latency_filtered_10_shards.groupby('levels').mean()

df_cross_latency_filtered_20_shards = df_cross_latency[
    (df_cross_latency["shards"] == 20) &
    (df_cross_latency["transaction_rate"] == 200) &
    (df_cross_latency["cross_shard_transaction_ratio"] == 0.25)
]

df_cross_latency_filtered_20_shards = df_cross_latency_filtered_20_shards.sort_values('levels')

df_cross_latency_filtered_20_shards_average = df_cross_latency_filtered_20_shards.groupby('levels').mean()

df_cross_latency_filtered_30_shards = df_cross_latency[
    (df_cross_latency["shards"] == 30) &
    (df_cross_latency["transaction_rate"] == 200) &
    (df_cross_latency["cross_shard_transaction_ratio"] == 0.25)
]

df_cross_latency_filtered_30_shards = df_cross_latency_filtered_30_shards.sort_values('levels')

df_cross_latency_filtered_30_shards_average = df_cross_latency_filtered_30_shards.groupby('levels').mean()

df_cross_latency_filtered_50_shards = df_cross_latency[
    (df_cross_latency["shards"] == 50) &
    (df_cross_latency["transaction_rate"] == 200) &
    (df_cross_latency["cross_shard_transaction_ratio"] == 0.25)
]

df_cross_latency_filtered_50_shards = df_cross_latency_filtered_50_shards.sort_values('levels')

df_cross_latency_filtered_50_shards_average = df_cross_latency_filtered_50_shards.groupby('levels').mean()

fig_cross_latency, ax_cross_latency = plt.subplots(nrows=2, ncols=3)

ax_cross_latency_5  =  df_cross_latency_filtered_5_shards_average.plot.bar(y="crossshard_latency", label="5 Shards", width=0.5, rot=0,  ax=ax_cross_latency[0,0], color="green", alpha=0.5, legend=False)
ax_cross_latency_10 = df_cross_latency_filtered_10_shards_average.plot.bar(y="crossshard_latency", label="10 Shards", width=0.5, rot=0, ax=ax_cross_latency[0,1], color="green", alpha=0.5, legend=False)
ax_cross_latency_20 = df_cross_latency_filtered_20_shards_average.plot.bar(y="crossshard_latency", label="20 Shards", width=0.5, rot=0, ax=ax_cross_latency[0,2], color="green", alpha=0.5, legend=False)
ax_cross_latency_30 = df_cross_latency_filtered_30_shards_average.plot.bar(y="crossshard_latency", label="30 Shards", width=0.5, rot=0, ax=ax_cross_latency[1,0], color="green", alpha=0.5, legend=False)
ax_cross_latency_50 = df_cross_latency_filtered_50_shards_average.plot.bar(y="crossshard_latency", label="50 Shards", width=0.5, rot=0, ax=ax_cross_latency[1,1], color="green", alpha=0.5, legend=False)

add_number_labels_bar_plot(ax_cross_latency_5)
add_number_labels_bar_plot(ax_cross_latency_10)
add_number_labels_bar_plot(ax_cross_latency_20)
add_number_labels_bar_plot(ax_cross_latency_30)
add_number_labels_bar_plot(ax_cross_latency_50)

ax_cross_latency[0,0].set_xlabel('Hierarchy levels')
ax_cross_latency[0,0].set_ylabel('Cross Shard Latency (s)')
ax_cross_latency[0,0].set_title('5 Shards')
ax_cross_latency[0,1].set_xlabel('Hierarchy levels')
ax_cross_latency[0,1].set_ylabel('Cross Shard Latency (s)')
ax_cross_latency[0,1].set_title('10 Shards')
ax_cross_latency[0,2].set_xlabel('Hierarchy levels')
ax_cross_latency[0,2].set_ylabel('Cross Shard Latency (s)')
ax_cross_latency[0,2].set_title('20 Shards')
ax_cross_latency[1,0].set_xlabel('Hierarchy levels')
ax_cross_latency[1,0].set_ylabel('Cross Shard Latency (s)')
ax_cross_latency[1,0].set_title('30 Shards')
ax_cross_latency[1,1].set_xlabel('Hierarchy levels')
ax_cross_latency[1,1].set_ylabel('Cross Shard Latency (s)')
ax_cross_latency[1,1].set_title('50 Shards')

ax_cross_latency[1,2].set_visible(False)

fig_cross_latency.tight_layout()

plt.show()

# df_cross_latency.plot(kind="line", x="cross_shard_transaction_ratio", y="crossshard_latency", color="red")

# cross_latency_3d_figure = plt.figure().gca(projection="3d")

# cross_latency_3d_figure.scatter(
#     df_cross_latency["children"],
#     df_cross_latency["shards"],
#     df_cross_latency["crossshard_latency"],
# )

# cross_latency_3d_figure.set_xlabel("children per shard")
# cross_latency_3d_figure.set_ylabel("shards")
# cross_latency_3d_figure.set_zlabel("crossshard_latency")

# plt.show()

# print(df_intra_throughput)
# print(df_intra_latency)
# print(df_cross_throughput)
# print(df_cross_latency)

import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy.stats import f

model_intra_throughput = ols(
    """
        intrashard_throughput ~ C(children) + C(levels) + C(transaction_rate) + C(cross_shard_transaction_ratio)
    """,
    data=df_intra_throughput_filtered,
).fit()

# model_intra_throughput = ols(
#     """intrashard_throughput ~ C(shards) + C(levels) + C(transaction_rate) + C(cross_shard_transaction_ratio) +
#             C(shards):C(levels) + C(shards):C(transaction_rate) + C(shards):C(cross_shard_transaction_ratio) +
#             C(levels):C(transaction_rate) + C(levels):C(cross_shard_transaction_ratio) + C(shards):C(levels):C(transaction_rate) +
#             C(shards):C(levels):C(transaction_rate):C(cross_shard_transaction_ratio)""",
#     data=df_intra_throughput,
# ).fit()

anova_table = sm.stats.anova_lm(model_intra_throughput, typ=2)

print(anova_table)

dfn = model_intra_throughput.df_model
dfd = model_intra_throughput.df_resid

# Calculate the critical F-value
alpha = 0.05  # significance level
f_critical = f.ppf(1 - alpha, dfn, dfd)
print(f"f-critical for first anova is {f_critical}")

print("Critical F-value:", f_critical)

model_intra_latency = ols(
    """
        intrashard_latency ~ C(children) + C(levels) + C(transaction_rate) + C(cross_shard_transaction_ratio)
    """,
    data=df_intra_latency_filtered,
).fit()

print(sm.stats.anova_lm(model_intra_latency, typ=2))

dfn = model_intra_latency.df_model
dfd = model_intra_latency.df_resid

# Calculate the critical F-value
alpha = 0.05  # significance level
f_critical = f.ppf(1 - alpha, dfn, dfd)
print(f"f-critical for first anova is {f_critical}")


model_cross_throughput = ols(
    """
        crossshard_throughput ~ C(children) + C(levels) + C(transaction_rate) + C(cross_shard_transaction_ratio)
    """,
    data=df_cross_throughput_filtered,
).fit()

print(sm.stats.anova_lm(model_cross_throughput, typ=2))

dfn = model_cross_throughput.df_model
dfd = model_cross_throughput.df_resid

# Calculate the critical F-value
alpha = 0.05  # significance level
f_critical = f.ppf(1 - alpha, dfn, dfd)
print(f"f-critical for first anova is {f_critical}")

model_cross_latency = ols(
    """
        crossshard_latency ~ C(children) + C(levels) + C(transaction_rate) + C(cross_shard_transaction_ratio)
    """,
    data=df_cross_latency,
).fit()

print(sm.stats.anova_lm(model_cross_latency, typ=2))

dfn = model_cross_latency.df_model
dfd = model_cross_latency.df_resid

# Calculate the critical F-value
alpha = 0.05  # significance level
f_critical = f.ppf(1 - alpha, dfn, dfd)
print(f"f-critical for first anova is {f_critical}")

import random
import hashlib
import uuid
import os
import sys

from collections import namedtuple

sys.path.insert(0, "..")

from new_shard_sim.ArchitectureGenerator import ArchitectureGenerator
from new_shard_sim.Transaction import Transaction


AMOUNT_OF_ADRESSES_PER_SHARD = 500
# 1 -> all transactions are cross shard
# 0 -> no crossshard transactions
CROSS_SHARD_TRANSACTION_RATIO = 0.1
AMOUNT_TRANSACTIONS = 30000
DATA_DIR = "precomputed_graphs"
STATIC_DATA_DIR = "static_data"


Combination = namedtuple("Combination", ["shards", "children", "levels"])

AMOUNT_OF_FILES_PER_COMBINATION = 5

POSSIBLE_COMBINATIONS = [
    Combination(5, 2, 3),
    Combination(5, 3, 3),
    Combination(5, 5, 2),
    Combination(5, 10, 2),
    Combination(10, 3, 3),
    Combination(10, 5, 3),
    Combination(10, 10, 2),
    Combination(15, 3, 4),
    Combination(15, 5, 3),
    Combination(15, 10, 3),
    Combination(20, 3, 4),
    Combination(20, 5, 3),
    Combination(20, 10, 3),
    Combination(30, 3, 4),
    Combination(30, 5, 3),
    Combination(30, 10, 3),
    Combination(50, 5, 4),
    Combination(50, 10, 3),
]


def find_amount_leaf_shards(number_shards, number_children, number_levels):
    _, shard_array = ArchitectureGenerator.generate_architecture(
        number_shards=number_shards, number_children=number_children, number_levels=number_levels
    )

    return len([shard for shard in shard_array if shard.children == []])


def create_address():
    hash = hashlib.sha1()
    hash.update(str(uuid.uuid4()).encode("utf-8"))
    hash_bytes = hash.digest()
    hash_hex = hash_bytes.hex()
    return f"0x{hash_hex[:40]}"


os.makedirs(DATA_DIR, exist_ok=True)

for file_number in range(AMOUNT_OF_FILES_PER_COMBINATION):
    for combination in POSSIBLE_COMBINATIONS:
        address_pools = {}
        amount_leaf_shards = find_amount_leaf_shards(combination.shards, combination.children, combination.levels)
        for i in range(amount_leaf_shards):
            address_pools[i] = []
            for _ in range(AMOUNT_OF_ADRESSES_PER_SHARD):
                address_pools[i].append(create_address())

        # code to generate intrashard transaction
        # asummng I want a balanced amount of transactions in each shard

        raw_transaction_list = []

        for i in range(AMOUNT_TRANSACTIONS):

            if i >= int(AMOUNT_TRANSACTIONS * CROSS_SHARD_TRANSACTION_RATIO):
                sample = random.sample(address_pools[i % amount_leaf_shards], 2)

                raw_transaction_list.append(
                    f"1723411	6	c37d1bac456e359ce696bb55107e7c8a701f71fe0b2bd83a5e8387b3690c1fe8	2016-06-18 00:00:02	0	call	{sample[0]}	{sample[1]}	1	105500282832602990	1.6173	105500282832602990	1.6173	478956950703000	0.0073	21000	90000	22807473843		1659669	1b	c0bb8aba13b5cb05fbd2952aa2d892fb0b39f247f96744dec7811f9d8ad05e0c	4d5b68e48792613464749dc16cc5c38b8c75186e2f795818298ebaa02d9a1813\n"
                )
            else:
                shards = random.sample(address_pools.keys(), 2)

                choice_0 = random.choice(address_pools[shards[0]])
                choice_1 = random.choice(address_pools[shards[1]])

                raw_transaction_list.append(
                    f"1723411	6	c37d1bac456e359ce696bb55107e7c8a701f71fe0b2bd83a5e8387b3690c1fe8	2016-06-18 00:00:02	0	call	{choice_0}	{choice_1}	1	105500282832602990	1.6173	105500282832602990	1.6173	478956950703000	0.0073	21000	90000	22807473843		1659669	1b	c0bb8aba13b5cb05fbd2952aa2d892fb0b39f247f96744dec7811f9d8ad05e0c	4d5b68e48792613464749dc16cc5c38b8c75186e2f795818298ebaa02d9a1813\n"
                )

        random.shuffle(raw_transaction_list)

        raw_transaction_list = [
            "block_id	index	hash	time	failed	type	sender	recipient	call_count	value	value_usd	internal_value	internal_value_usd	fee	fee_usd	gas_used	gas_limit	gas_price	input_hex	nonce	v	r	s\n"
        ] + raw_transaction_list

        os.makedirs(f"{DATA_DIR}/{amount_leaf_shards}", exist_ok=True)

        file_prefix = f"{combination.shards}-{combination.children}-{combination.levels}-{file_number}"

        with open(f"{STATIC_DATA_DIR}/{file_prefix}-txs-file.tsv", "a") as f:
            f.writelines(raw_transaction_list)

        with open(f"{DATA_DIR}/{amount_leaf_shards}/{file_prefix}-txs_graph_nodes.txt", "a") as f:
            for key in address_pools.keys():
                for address in address_pools[key]:
                    f.write(f"{address}\n")

            f.close()

        with open(f"{DATA_DIR}/{amount_leaf_shards}/{file_prefix}-labels.txt", "a") as f:
            for key in address_pools.keys():
                for _ in address_pools[key]:
                    f.write(str(key) + "\n")

            f.close()

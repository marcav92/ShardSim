import time
import datetime
from shard_sim.Constants import *


class TransactionPreprocessor:
    def __init__(self):
        self.raw_transactions = []

    def get_raw_transactions(self):
        return self.raw_transactions

    def load_transactions_from_file(self, file_name):
        with open(file_name) as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                if idx == 0:
                    continue
                line_array = line.split("\t")

                if line_array[6] == "\\N" or line_array[7] == "\\N":
                    continue

                self.raw_transactions.append(
                    {
                        "timestamp": TransactionPreprocessor.str_to_timestamp(line_array[3]),
                        "sender": line_array[6],  # 6 is the position of the sender address  in the tsv file
                        "recipient": line_array[7],  # 7 is     the position of the recipient address
                        "amount": float(line_array[10]),
                    }
                )

    def str_to_timestamp(time_string):
        date_time_obj = datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
        return time.mktime(date_time_obj.timetuple()) * 1000

    def assign_accounts_to_shards(self, topology):
        shard_array = topology.get_shards(WORKER)

        for transaction in self.raw_transactions:
            if transaction["sender"] not in topology.addresses_map:
                # assignment of accounts to shards
                assigned_shard = int(transaction["sender"], base=16) % len(shard_array)

                topology.addresses_map[transaction["sender"]] = assigned_shard
                shard_array[assigned_shard].add_account(transaction["sender"])

            if transaction["recipient"] not in topology.addresses_map:
                # assignment of accounts to shards
                assigned_shard = int(transaction["recipient"], base=16) % len(shard_array)

                topology.addresses_map[transaction["recipient"]] = assigned_shard
                shard_array[assigned_shard].add_account(transaction["recipient"])


if __name__ == "__main__":
    preprocessor = TransactionPreprocessor()
    preprocessor.load_transactions_from_file("static_data/data")
    print(type(preprocessor.raw_transactions[100]["sender"]))

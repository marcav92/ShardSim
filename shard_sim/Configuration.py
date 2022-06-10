class Config:

    worker_block_interval = 600  # this figure is defined in seconds
    intrashard_comm_delay_upper_bound = 60  # this figure is defined in seconds
    transactions_per_block = 715  # 15 000 000 / 21 000
    cross_shard_transactions_per_block = 1000
    commitments_per_block = 20

    @classmethod
    def init(cls, **args):
        cls.worker_block_interval = args["worker_block_interval"] if "worker_block_interval" in args else 600
        cls.intrashard_comm_delay_upper_bound = (
            args["intrashard_comm_delay_upper_bound"] if "intrashard_comm_delay_upper_bound" in args else 60
        )
        cls.transactions_per_block = args["transactions_per_block"] if "transactions_per_block" in args else 715
        cls.cross_shard_transactions_per_block = (
            args["cross_shard_transactions_per_block"] if "cross_shard_transactions_per_block" in args else 1000
        )
        cls.commitments_per_block = args["commitments_per_block"] if "commitments_per_block" in args else 20

    @classmethod
    def print_config(cls):
        print(
            f"""
            worker_block_interval:              {cls.worker_block_interval}
            intrashard_comm_delay_upper_bound:  {cls.intrashard_comm_delay_upper_bound}
            transactions_per_block:             {cls.transactions_per_block}
            cross_shard_transactions_per_block: {cls.cross_shard_transactions_per_block}
            commitments_per_block:              {cls.commitments_per_block}
            """
        )

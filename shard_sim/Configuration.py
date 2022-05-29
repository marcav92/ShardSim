class Config:

    worker_block_interval = 600  # this figure is defined in seconds
    intrashard_comm_delay_upper_bound = 60  # this figure is defined in seconds
    transactions_per_block = 715  # 15 000 000 / 21 000

    @classmethod
    def init(cls, **args):
        cls.worker_block_interval = args["worker_block_interval"] if "worker_block_interval" in args else 600
        cls.intrashard_comm_delay_upper_bound = (
            args["intrashard_comm_delay_upper_bound"] if "intrashard_comm_delay_upper_bound" in args else 60
        )
        cls.transactions_per_block = args["transactions_per_block"] if "transactions_per_block" in args else 715

    @classmethod
    def print_config(cls):
        print(
            f"""
        worker_block_interval:                     {cls.worker_block_interval}
        intrashard_comm_delay_upper_bound:  {cls.intrashard_comm_delay_upper_bound}
        transactions_per_block: {cls.transactions_per_block}
      """
        )

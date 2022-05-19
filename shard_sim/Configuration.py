class Config:

    block_interval = 600  # this figure is defined in seconds
    intrashard_comm_delay_upper_bound = 60  # this figure is defined in seconds

    @classmethod
    def init(cls, **args):
        cls.block_interval = (
            args["block_interval"] if "block_interval" in args else 1000
        )
        cls.intrashard_comm_delay_upper_bound = (
            args["intrashard_comm_delay_upper_bound"]
            if "intrashard_comm_delay_upper_bound" in args
            else 60
        )

    @classmethod
    def print_config(cls):
        print(
            f"""
        block_interval:                     {cls.block_interval}
        intrashard_comm_delay_upper_bound:  {cls.intrashard_comm_delay_upper_bound}
      """
        )

from new_shard_sim.Topology import Topology
from new_shard_sim.Constants import *


class Logger:
    directory = ""

    @classmethod
    def init(cls, directory):
        cls.directory = directory

    @classmethod
    def log_message(cls, module, timestamp, message, shard_id=None):
        if DEBUG:
            shard_name = ""
            if shard_id:
                shard_name = Topology.shard_map[str(shard_id)].name
            with open(f"{cls.directory}/sim-{module}.log", "a") as file:
                file.write(f"{shard_name} {timestamp}: {message}\n")
                file.close()

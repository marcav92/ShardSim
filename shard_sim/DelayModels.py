import random

from shard_sim.Constants import *
from shard_sim.Configuration import Config


class DelayModel:
    def exponential_delay(type):

        if type == INTRA_SHARD_DELAY:
            return random.expovariate(1) * Config.intrashard_comm_delay_upper_bound

        elif type == WORKER_REFERENCE_COMM_DELAY:
            return random.expovariate(1.5) * Config.intrashard_comm_delay_upper_bound

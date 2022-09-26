import random

from new_shard_sim.Constants import *


class ComunicationDelay:
    def exponential_delay():
        return int(random.expovariate(CST_EXP_DELAY_LAMBDA) * 1000)

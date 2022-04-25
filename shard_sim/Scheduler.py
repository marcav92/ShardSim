#reference of queue
#should be able to read csv with transactions
#should schedule block generation depending on a list of nodes from the simulation
#should schedule block generation based on a specified frequency
#should schedule block generation with jitter

#should be able to handle several frequencies depending if the node belongs to
#reference shard or worker shard.

#might need to schedule data reception events


class Scheduler():

    def __init__(self, 
        simulation_queue, 
        nodes_list,
        reference_node_frequency,
        worker_node_frequency,
        with_jitter,
        ):
        pass

    def load_transactions_csv():
        
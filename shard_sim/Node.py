import uuid


from shard_sim.Block import Block, BlockRivetReference, BlockRivetWorker
from shard_sim.Event import Event
from shard_sim.Queue import Queue
from shard_sim.Configuration import Config
from shard_sim.Transaction import Transaction, TransactionRivetCrossShard
from shard_sim.Shard import Shard, Shard_Rivet
from shard_sim.DelayModels import DelayModel
from shard_sim.Constants import *
import time


class SimulationLogger:
    def __init__(self):
        self.event_log = []

    def log_event(self, event):
        self.event_log.append(event)


class NodeBase(SimulationLogger):
    def __init__(self, id=None):
        super().__init__()
        self.id = id if id else uuid.uuid4()
        self.membership = ""
        self.intrashard_neighbors = []
        self.crossshard_neighbors = []

    def add_intrashard_neighbor(self, node):
        self.intrashard_neighbors.append(node)

    def add_crossshard_neighbor(self, node):
        self.crossshard_neighbors.append(node)

    def set_membership(self, shard_id):
        self.membership = shard_id


class NodeL1(NodeBase):
    def __init__(self, id=None):
        super().__init__(id)
        self.transactions_pool = []

    def __repr__(self):
        return f"""
            id                  :   {self.id}
            transactionPool     :   {self.transactions_pool}
            intrashard neighbors:   {self.intrashard_neighbors}
        """

    def receive_event_L1(self, event):
        if event.type == EVT_RECEIVE_TRANSACTION:
            self.propagate_transaction(event)

        else:
            raise Exception("Event type cant be handled at layer 1")

    def reset_state_transactions_pool(nodes_list):
        for node in nodes_list:
            node.transactions_pool = []

    def propagate_transaction(self, event):

        # events could have several types i.e transaction, block
        if event.data.id not in [transaction.id for transaction in self.transactions_pool]:
            for node in self.intrashard_neighbors:
                # create function to calculate time delay
                Queue.add_event(
                    Event(
                        EVT_RECEIVE_TRANSACTION,
                        node.id,
                        event.time + 0.5,
                        event.data,
                        event.id,
                    )
                )
                self.log_event(event)
            self.transactions_pool.append(event.data)


class NodeL2BasicHotStuff(NodeL1):
    def __init__(self, id=None):
        super().__init__(id)
        self.blockchain = []
        self.shard = None
        self.view_number = 0
        self.current_view_number = 0
        self.new_view_messages = 0
        self.prepare_vote_messages = 0
        self.precommit_vote_messages = 0
        self.commit_vote_messages = 0
        self.current_phase = PREPARE
        self.is_leader = False

    def reset_hot_stuff_bookeeping_variables(self):
        self.current_phase = PREPARE
        self.new_view_messages = 0
        self.prepare_vote_messages = 0
        self.precommit_vote_messages = 0
        self.commit_vote_messages = 0
        self.is_leader = False

    def define_shard(self, shard):
        self.shard = shard

    def set_view_number(self, number):
        self.view_number = number

    def generate_genesis_block(nodes_list):
        for node in nodes_list:
            node.blockchain.append(Block())

    def get_last_block(self):
        return self.blockchain[len(self.blockchain) - 1]

    def get_blockchain_length(self):
        return len(self.blockchain) - 1

    # ==================================
    # basic hot stuff protocol
    # ==================================

    def broadcast_message(self, event, message):
        for node in self.shard.nodes:
            if node.id == self.id:
                continue
            else:
                # TODO: Add time delay function
                Queue.add_event(
                    Event(
                        EVT_REFERENCE_HOT_STUFF_MESSAGE,
                        node.id,
                        event.time + 25,
                        message,
                    )
                )

    def create_next_view_interrupt(self, event):
        Queue.add_event(
            Event(
                EVT_REFERENCE_HOT_STUFF_MESSAGE,
                self.id,
                event.time + 2500,
                {
                    "type": EVT_REFERENCE_HOT_STUFF_NEXT_VIEW_INTERRUPT,
                    "current_phase": self.current_phase,
                    "current_view_number": self.current_view_number,
                },
            )
        )

    def receive_event_L2(self, event):
        if event.data["type"] == EVT_REFERENCE_HOT_STUFF_NEW_VIEW_MESSAGE:
            self.hot_stuff_receive_new_view_message(event)

        elif event.data["type"] == EVT_REFERENCE_HOT_STUFF_PREPARE_MESSAGE:
            self.hot_stuff_receive_prepare_message(event)

        elif event.data["type"] == EVT_REFERENCE_HOT_STUFF_PREPARE_VOTE_MESSAGE:
            self.hot_stuff_receive_prepare_vote_message(event)

        elif event.data["type"] == EVT_REFERENCE_HOT_STUFF_PRECOMMIT_MESSAGE:
            self.hot_stuff_receive_precommit_message(event)

        elif event.data["type"] == EVT_REFERENCE_HOT_STUFF_PRECOMMIT_VOTE_MESSAGE:
            self.hot_stuff_receive_precommit_vote_message(event)

        elif event.data["type"] == EVT_REFERENCE_HOT_STUFF_COMMIT_MESSAGE:
            self.hot_stuff_receive_commit_message(event)

        elif event.data["type"] == EVT_REFERENCE_HOT_STUFF_COMMIT_VOTE_MESSAGE:
            self.hot_stuff_receive_commit_vote_message(event)

        elif event.data["type"] == EVT_REFERENCE_HOT_STUFF_DECIDE_MESSAGE:
            self.hot_stuff_receive_decide_message(event)

        elif event.data["type"] == EVT_REFERENCE_HOT_STUFF_NEXT_VIEW_INTERRUPT:
            self.hot_stuff_receive_next_view_interrupt(event)

    def hot_stuff_receive_new_view_message(self, event):

        if self.current_phase == PREPARE and event.data["current_view_number"] >= self.current_view_number:
            self.new_view_messages += 1

            if self.new_view_messages >= self.shard.get_n_f_value():
                self.is_leader = True

                message = {
                    "type": EVT_REFERENCE_HOT_STUFF_PREPARE_MESSAGE,
                    "current_view_number": self.current_view_number
                    # it oculd be necessary to put more details in here
                }
                self.broadcast_message(event, message)

                self.current_phase = PRECOMMIT
                self.create_next_view_interrupt(event)

    def hot_stuff_receive_prepare_message(self, event):
        # determine if the PREPARE message should be accepted
        if self.current_phase == PREPARE and event.data["current_view_number"] >= self.current_view_number:
            Queue.add_event(
                Event(
                    EVT_REFERENCE_HOT_STUFF_MESSAGE,
                    self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                    event.time + 25,
                    {
                        "type": EVT_REFERENCE_HOT_STUFF_PREPARE_VOTE_MESSAGE,
                        "current_view_number": self.current_view_number,
                    },
                )
            )

            self.current_phase = PRECOMMIT
            self.create_next_view_interrupt(event)

    def hot_stuff_receive_prepare_vote_message(self, event):
        if self.current_phase == PRECOMMIT and event.data["current_view_number"] >= self.current_view_number:
            self.prepare_vote_messages += 1

            if self.prepare_vote_messages >= self.shard.get_n_f_value():
                # broadcast pre-commit

                message = {
                    "type": EVT_REFERENCE_HOT_STUFF_PRECOMMIT_MESSAGE,
                    "current_view_number": self.current_view_number
                    # it oculd be necessary to put more details in here
                }
                self.broadcast_message(event, message)

                self.current_phase = COMMIT
                self.create_next_view_interrupt(event)

    def hot_stuff_receive_precommit_message(self, event):
        if self.current_phase == PRECOMMIT and event.data["current_view_number"] >= self.current_view_number:
            Queue.add_event(
                Event(
                    EVT_REFERENCE_HOT_STUFF_MESSAGE,
                    self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                    event.time + 25,
                    {
                        "type": EVT_REFERENCE_HOT_STUFF_PRECOMMIT_VOTE_MESSAGE,
                        "current_view_number": self.current_view_number,
                    },
                )
            )

            self.current_phase = COMMIT
            self.create_next_view_interrupt(event)

    def hot_stuff_receive_precommit_vote_message(self, event):
        if self.current_phase == COMMIT and event.data["current_view_number"] >= self.current_view_number:
            self.precommit_vote_messages += 1

            if self.precommit_vote_messages >= self.shard.get_n_f_value():
                # broadcast commit
                message = {
                    "type": EVT_REFERENCE_HOT_STUFF_COMMIT_MESSAGE,
                    # it oculd be necessary to put more details in here
                    "current_view_number": self.current_view_number,
                }
                self.broadcast_message(event, message)

                self.current_phase = DECIDE
                self.create_next_view_interrupt(event)

    def hot_stuff_receive_commit_message(self, event):
        if self.current_phase == COMMIT and event.data["current_view_number"] >= self.current_view_number:

            Queue.add_event(
                Event(
                    EVT_REFERENCE_HOT_STUFF_MESSAGE,
                    self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                    event.time + 25,
                    {
                        "type": EVT_REFERENCE_HOT_STUFF_COMMIT_VOTE_MESSAGE,
                        "current_view_number": self.current_view_number,
                    },
                )
            )

            self.current_phase = DECIDE
            self.create_next_view_interrupt(event)

    def hot_stuff_receive_commit_vote_message(self, event):
        if self.current_phase == DECIDE and event.data["current_view_number"] >= self.current_view_number:

            self.commit_vote_messages += 1

            if self.commit_vote_messages >= self.shard.get_n_f_value():
                # broadcast commit
                message = {
                    "type": EVT_REFERENCE_HOT_STUFF_DECIDE_MESSAGE,
                    "current_view_number": self.current_view_number
                    # it oculd be necessary to put more details in here
                }
                self.broadcast_message(event, message)

                self.reset_hot_stuff_bookeeping_variables()
                self.create_next_view_interrupt(event)

                self.current_view_number += 1

                if (self.current_view_number % self.shard.n_value) != self.view_number:
                    Queue.add_event(
                        Event(
                            EVT_REFERENCE_HOT_STUFF_MESSAGE,
                            self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                            event.time + 25,
                            {
                                "type": EVT_REFERENCE_HOT_STUFF_NEW_VIEW_MESSAGE,
                                "current_view_number": self.current_view_number,
                            },
                        )
                    )

    def hot_stuff_receive_decide_message(self, event):

        if self.current_phase == DECIDE and event.data["current_view_number"] >= self.current_view_number:

            self.reset_hot_stuff_bookeeping_variables()
            self.create_next_view_interrupt(event)

            self.current_view_number += 1

            if (self.current_view_number % self.shard.n_value) != self.view_number:
                Queue.add_event(
                    Event(
                        EVT_REFERENCE_HOT_STUFF_MESSAGE,
                        self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                        event.time + 25,
                        {
                            "type": EVT_REFERENCE_HOT_STUFF_NEW_VIEW_MESSAGE,
                            "current_view_number": self.current_view_number,
                        },
                    )
                )

    def hot_stuff_receive_next_view_interrupt(self, event):

        if (
            self.current_phase == event.data["current_phase"]
            and event.data["current_view_number"] >= self.current_view_number
        ):
            self.current_phase = PREPARE
            self.create_next_view_interrupt(event)

            self.current_view_number += 1

            if (self.current_view_number % self.shard.n_value) != self.view_number:

                Queue.add_event(
                    Event(
                        EVT_REFERENCE_HOT_STUFF_MESSAGE,
                        self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                        event.time + 25,
                        {
                            "type": EVT_REFERENCE_HOT_STUFF_NEW_VIEW_MESSAGE,
                            "current_view_number": self.current_view_number,
                        },
                    )
                )


class NodeL2Rivet(NodeL1):
    def __init__(self, type, id=None):
        super().__init__(id)
        # configuration attributes
        self.shard: Shard_Rivet = None
        self.type = type
        self.view_number = 0
        self.current_view_number = 0
        self.blockchain: list[BlockRivetWorker] = []
        self.is_leader = False

        if type == REFERENCE:
            # protocol bookkeeping variables
            self.new_view_messages = 0
            self.prepare_vote_messages = 0
            self.precommit_vote_messages = 0
            self.commit_vote_messages = 0
            self.current_phase = PREPARE

            self.receive_event_L2 = self.reference_receive_event_L2

        elif type == WORKER:

            self.current_phase = CERTIFICATION
            self.receive_event_L2 = self.worker_receive_event_L2
            self.latest_known_reference_block: BlockRivetReference = None

    # general purpose helper functions

    def define_shard(self, shard):
        self.shard = shard

    def set_view_number(self, number):
        self.view_number = number

    def generate_genesis_block(self):
        self.generate_block(0, self.id, [])

    def get_last_block(self):
        return self.blockchain[len(self.blockchain) - 1]

    def get_block_at_height(self, height):
        return self.blockchain[height - 1]

    def get_blockchain_length(self):
        return len(self.blockchain)

    def broadcast_message(self, event, message):
        for node in self.shard.nodes:
            if node.id == self.id:
                continue
            else:
                # TODO: Add time delay function
                Queue.add_event(
                    Event(
                        EVT_REFERENCE_RIVET_MESSAGE,
                        node.id,
                        event.time + 25,
                        message,
                    )
                )

    # reference shard helper functions
    def generate_reference_block(self, timestamp, node_id, block_transactions):
        self.blockchain.append(
            BlockRivetReference(
                height=self.get_blockchain_length() + 1,
                previous=self.get_last_block().hash,
                timestamp=timestamp,
                minter=node_id,
                transactions=block_transactions,
            )
        )

    def reference_reset_bookeeping_variables(self):
        self.current_phase = PREPARE
        self.new_view_messages = 0
        self.prepare_vote_messages = 0
        self.precommit_vote_messages = 0
        self.commit_vote_messages = 0
        self.is_leader = False

    def reference_create_next_view_interrupt(self, event):
        Queue.add_event(
            Event(
                EVT_REFERENCE_RIVET_MESSAGE,
                self.id,
                # TODO: Add time delay function
                event.time + 2500,
                {
                    "type": EVT_REFERENCE_RIVET_NEXT_VIEW_INTERRUPT,
                    "current_phase": self.current_phase,
                    "current_view_number": self.current_view_number,
                },
            )
        )

    def reference_receive_event_L2(self, event):
        if event.data["type"] == EVT_REFERENCE_RIVET_NEW_VIEW_MESSAGE:
            self.reference_receive_new_view_message(event)

        elif event.data["type"] == EVT_REFERENCE_RIVET_PREPARE_MESSAGE:
            self.reference_receive_prepare_message(event)

        elif event.data["type"] == EVT_REFERENCE_RIVET_PREPARE_VOTE_MESSAGE:
            self.reference_receive_prepare_vote_message(event)

        elif event.data["type"] == EVT_REFERENCE_RIVET_PRECOMMIT_MESSAGE:
            self.reference_receive_precommit_message(event)

        elif event.data["type"] == EVT_REFERENCE_RIVET_PRECOMMIT_VOTE_MESSAGE:
            self.reference_receive_precommit_vote_message(event)

        elif event.data["type"] == EVT_REFERENCE_RIVET_COMMIT_MESSAGE:
            self.reference_receive_commit_message(event)

        elif event.data["type"] == EVT_REFERENCE_RIVET_COMMIT_VOTE_MESSAGE:
            self.reference_receive_commit_vote_message(event)

        elif event.data["type"] == EVT_REFERENCE_RIVET_DECIDE_MESSAGE:
            self.reference_receive_decide_message(event)

        elif event.data["type"] == EVT_REFERENCE_RIVET_NEXT_VIEW_INTERRUPT:
            self.reference_receive_next_view_interrupt(event)

    def worker_receive_event_L2(self, event):
        if event.data["type"] == EVT_WORKER_RIVET_PROPOSAL_MESSAGE:
            self.worker_receive_proposal_message(event)

        elif event.data["type"] == EVT_WORKER_RIVET_CERTIFICATION_MESSAGE:
            self.worker_receive_certification_message(event)

        elif event.data["type"] == EVT_WORKER_RIVET_CERTIFICATION_VOTE_MESSAGE:
            self.worker_receive_certification_vote_message(event)

    def reference_receive_new_view_message(self, event):

        if self.current_phase == PREPARE and event.data["current_view_number"] >= self.current_view_number:
            self.new_view_messages += 1
            if self.new_view_messages >= self.shard.get_n_f_value():
                self.is_leader = True

                message = {
                    "type": EVT_REFERENCE_RIVET_PREPARE_MESSAGE,
                    "current_view_number": self.current_view_number
                    # it oculd be necessary to put more details in here
                }
                self.broadcast_message(event, message)

                self.current_phase = PRECOMMIT
                self.reference_create_next_view_interrupt(event)

    def reference_receive_prepare_message(self, event):
        # determine if the PREPARE message should be accepted
        if self.current_phase == PREPARE and event.data["current_view_number"] >= self.current_view_number:
            Queue.add_event(
                Event(
                    EVT_REFERENCE_RIVET_MESSAGE,
                    self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                    event.time + 25,
                    {
                        "type": EVT_REFERENCE_RIVET_PREPARE_VOTE_MESSAGE,
                        "current_view_number": self.current_view_number,
                    },
                )
            )

            self.current_phase = PRECOMMIT
            self.reference_create_next_view_interrupt(event)

    def reference_receive_prepare_vote_message(self, event):
        if self.current_phase == PRECOMMIT and event.data["current_view_number"] >= self.current_view_number:
            self.prepare_vote_messages += 1

            if self.prepare_vote_messages >= self.shard.get_n_f_value():
                # broadcast pre-commit

                message = {
                    "type": EVT_REFERENCE_RIVET_PRECOMMIT_MESSAGE,
                    "current_view_number": self.current_view_number
                    # it oculd be necessary to put more details in here
                }
                self.broadcast_message(event, message)

                self.current_phase = COMMIT
                self.reference_create_next_view_interrupt(event)

    def reference_receive_precommit_message(self, event):
        if self.current_phase == PRECOMMIT and event.data["current_view_number"] >= self.current_view_number:
            Queue.add_event(
                Event(
                    EVT_REFERENCE_RIVET_MESSAGE,
                    self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                    event.time + 25,
                    {
                        "type": EVT_REFERENCE_RIVET_PRECOMMIT_VOTE_MESSAGE,
                        "current_view_number": self.current_view_number,
                    },
                )
            )

            self.current_phase = COMMIT
            self.reference_create_next_view_interrupt(event)

    def reference_receive_precommit_vote_message(self, event):
        if self.current_phase == COMMIT and event.data["current_view_number"] >= self.current_view_number:
            self.precommit_vote_messages += 1

            if self.precommit_vote_messages >= self.shard.get_n_f_value():
                # broadcast commit
                message = {
                    "type": EVT_REFERENCE_RIVET_COMMIT_MESSAGE,
                    # it oculd be necessary to put more details in here
                    "current_view_number": self.current_view_number,
                }
                self.broadcast_message(event, message)

                self.current_phase = DECIDE
                self.reference_create_next_view_interrupt(event)

    def reference_receive_commit_message(self, event):
        if self.current_phase == COMMIT and event.data["current_view_number"] >= self.current_view_number:

            Queue.add_event(
                Event(
                    EVT_REFERENCE_RIVET_MESSAGE,
                    self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                    event.time + 25,
                    {
                        "type": EVT_REFERENCE_RIVET_COMMIT_VOTE_MESSAGE,
                        "current_view_number": self.current_view_number,
                    },
                )
            )

            self.current_phase = DECIDE
            self.reference_create_next_view_interrupt(event)

    def reference_receive_commit_vote_message(self, event):
        if self.current_phase == DECIDE and event.data["current_view_number"] >= self.current_view_number:

            self.commit_vote_messages += 1

            if self.commit_vote_messages >= self.shard.get_n_f_value():
                # broadcast commit
                message = {
                    "type": EVT_REFERENCE_RIVET_DECIDE_MESSAGE,
                    "current_view_number": self.current_view_number
                    # it oculd be necessary to put more details in here
                }
                self.broadcast_message(event, message)

                self.reference_reset_bookeeping_variables()
                self.reference_create_next_view_interrupt(event)

                self.current_view_number += 1

                if (self.current_view_number % self.shard.n_value) != self.view_number:
                    Queue.add_event(
                        Event(
                            EVT_REFERENCE_RIVET_MESSAGE,
                            self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                            event.time + 25,
                            {
                                "type": EVT_REFERENCE_RIVET_NEW_VIEW_MESSAGE,
                                "current_view_number": self.current_view_number,
                            },
                        )
                    )

    def reference_receive_decide_message(self, event):

        if self.current_phase == DECIDE and event.data["current_view_number"] >= self.current_view_number:

            self.reference_reset_bookeeping_variables()
            self.reference_create_next_view_interrupt(event)

            self.current_view_number += 1

            if (self.current_view_number % self.shard.n_value) != self.view_number:
                Queue.add_event(
                    Event(
                        EVT_REFERENCE_RIVET_MESSAGE,
                        self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                        event.time + 25,
                        {
                            "type": EVT_REFERENCE_RIVET_NEW_VIEW_MESSAGE,
                            "current_view_number": self.current_view_number,
                        },
                    )
                )

    def reference_receive_next_view_interrupt(self, event):

        if (
            self.current_phase == event.data["current_phase"]
            and event.data["current_view_number"] >= self.current_view_number
        ):
            self.current_phase = PREPARE
            self.reference_create_next_view_interrupt(event)

            self.current_view_number += 1

            if (self.current_view_number % self.shard.n_value) != self.view_number:

                Queue.add_event(
                    Event(
                        EVT_REFERENCE_RIVET_MESSAGE,
                        self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                        event.time + 25,
                        {
                            "type": EVT_REFERENCE_RIVET_NEW_VIEW_MESSAGE,
                            "current_view_number": self.current_view_number,
                        },
                    )
                )

    def reference_receive_data_request(self, event: Event):
        # Event(
        #     EVT_REFERENCE_RIVET_MESSAGE,
        #     node.id,
        #     event.time + 25,
        #     message,
        # )
        Queue.add_event(
            Event(
                event.data["parent_event"].type,
                event.data["parent_event"].node_id,
                event.time + DelayModel.exponential_delay(WORKER_REFERENCE_COMM_DELAY),
                {
                    "type": event.data["parent_event"]["data"]["type"],
                    "current_view_number": event.data["current_view_number"],
                },
            )
        )
        event.data["parent_event"]

    # worker helper functions

    def get_latest_reference_block(self, event):
        neighbor: NodeL2Rivet
        for neighbor in self.crossshard_neighbors:
            if neighbor.is_leader:
                Queue.add_event(
                    Event(
                        EVT_REFERENCE_RIVET_MESSAGE,
                        neighbor.id,
                        event.time + DelayModel.exponential_delay(WORKER_REFERENCE_COMM_DELAY),
                        {
                            "type": EVT_REFERENCE_DATA_REQUEST,
                            "parent_event": event,
                            "current_view_number": self.current_view_number,
                        },
                    )
                )

        # neighbor: NodeL2Rivet
        # for neighbor in self.crossshard_neighbors:
        #     if neighbor.is_leader:
        #         return neighbor.get_block_at_height(height)

    def extract_intrashard__txs_from_transaction_pool(self):
        not_consumed_transactions = self.transactions_pool[: Config.transactions_per_block]
        consumed_transactions = self.transactions_pool[: Config.transactions_per_block]
        self.transactions_pool = not_consumed_transactions
        return consumed_transactions

    def get_latest_committed_worker_block(self):
        block: BlockRivetWorker
        for block in self.blockchain[::-1]:
            if block.is_committed:
                return block

        return self.get_last_block()

    def generate_worker_block(self, timestamp, node_id, block_transactions, latest_known_ref_block_height):
        self.blockchain.append(
            BlockRivetWorker(
                height=self.get_blockchain_length() + 1,
                previous=self.get_last_block().hash,
                timestamp=timestamp,
                minter=node_id,
                transactions=block_transactions,
                latest_known_ref_block_height=latest_known_ref_block_height,
            )
        )

    def execute_transactions(self):
        """
        this function will execute both intrashard and crossshard transactions

        """
        latest_block = self.get_latest_committed_block()
        new_state = latest_block.state.copy()

        # cross shard transaction execution

        # will need to implement get_cross_shard_transaction since last commitment
        cross_shard_transactions = []

        cross_shard_transaction: TransactionRivetCrossShard

        for cross_shard_transaction in cross_shard_transactions:
            if cross_shard_transaction.sender in self.shard.account_set:
                new_state[cross_shard_transaction.sender] -= cross_shard_transaction.amount

            elif cross_shard_transaction.receiver in self.shard.account_set:
                new_state[cross_shard_transaction.receiver] += cross_shard_transaction.amount

        intra_shard_transaction: Transaction

        for intra_shard_transaction in self.transactions_pool:
            # what happens if sender balance is not enough
            new_state[intra_shard_transaction.sender] -= intra_shard_transaction.amount
            new_state[intra_shard_transaction.receiver] += intra_shard_transaction.amount

        return new_state

    def worker_receive_proposal_message(self, event):

        b_i: BlockRivetWorker = self.get_latest_committed_worker_block()
        p_i: BlockRivetReference = self.latest_known_reference_block

        b_j: BlockRivetWorker = self.get_last_block()
        # p_j: BlockRivetReference = self.get_reference_block_at_height(b_j.latest_known_ref_block_height)

        # last step
        # create proposal message for the next leader leader
        Queue.add_event(
            Event(
                EVT_REFERENCE_RIVET_MESSAGE,
                self.shard.view_id_map_lookup(self.current_view_number),
                event.time + Config.worker_block_interval,
                {
                    "type": EVT_WORKER_RIVET_PROPOSAL_MESSAGE,
                    "current_view_number": self.current_view_number,
                },
            )
        )

    def worker_receive_certification_message(self, event):
        # determine if the PREPARE message should be accepted
        pass

    def worker_receive_certification_vote_message(self, event):
        # determine if the PREPARE message should be accepted
        pass

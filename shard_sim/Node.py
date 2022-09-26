from hashlib import new
import uuid


from shard_sim.Block import Block, BlockRivetReference, BlockRivetWorker
from shard_sim.Event import Event
from shard_sim.Queue import Queue
from shard_sim.Configuration import Config
from shard_sim.Transaction import Transaction, TransactionRivetCrossShard
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
                        event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
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
        if self.blockchain:
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
                        event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
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
        self.shard = None
        self.type = type
        self.view_number = 0
        self.current_view_number = 0
        self.blockchain: list[BlockRivetWorker] = []
        self.is_leader = False
        self.last_proposed_block = None
        self.last_proposed_received_block = None

        if type == REFERENCE:
            # protocol bookkeeping variables
            self.new_view_messages = 0
            self.prepare_vote_messages = 0
            self.precommit_vote_messages = 0
            self.commit_vote_messages = 0
            self.current_phase = PREPARE
            # shard_id -> {block_id, state}
            self.commitments_pool = []

            self.receive_event_L2 = self.reference_receive_event_L2

        elif type == WORKER:

            self.current_phase = CERTIFICATION
            self.receive_event_L2 = self.worker_receive_event_L2
            self.latest_known_reference_block: BlockRivetReference = None
            self.waiting_for_data = False
            self.certification_votes = 0

    # general purpose helper functions

    def define_shard(self, shard):
        self.shard = shard

    def set_view_number(self, number):
        self.view_number = number

    def generate_genesis_block(self):
        if self.type == WORKER:
            self.generate_worker_block(0, self.id, [])
        elif self.type == REFERENCE:
            self.generate_reference_block(0, self.id, [], {})

    def get_last_block(self):
        if self.blockchain:
            return self.blockchain[-1]
        else:
            return None

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
                        event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
                        message,
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

        elif event.data["type"] == EVT_REFERENCE_RIVET_DATA_REQUEST:
            self.reference_receive_data_request(event)

        elif event.data["type"] == EVT_REFERENCE_COMMIT_BLOCK_STATE:
            self.reference_receive_commit_block_state(event)

    def worker_receive_event_L2(self, event):
        if event.data["type"] == EVT_WORKER_RIVET_PROPOSAL_MESSAGE:
            self.worker_receive_proposal_message(event)

        elif event.data["type"] == EVT_WORKER_RIVET_CERTIFICATION_MESSAGE:
            self.worker_receive_certification_message(event)

        elif event.data["type"] == EVT_WORKER_RIVET_CERTIFICATION_VOTE_MESSAGE:
            self.worker_receive_certification_vote_message(event)

    # reference shard helper functions

    def generate_reference_block(self, timestamp, node_id, block_transactions, commitments):
        self.blockchain.append(
            BlockRivetReference(
                height=self.get_blockchain_length() + 1,
                previous=self.get_last_block().hash if self.get_last_block() else None,
                timestamp=timestamp,
                minter=node_id,
                transactions=block_transactions,
                # commitments=commitments,
            )
        )

    def reference_reset_bookeeping_variables(self):
        self.current_phase = PREPARE
        self.new_view_messages = 0
        self.prepare_vote_messages = 0
        self.precommit_vote_messages = 0
        self.commit_vote_messages = 0
        self.is_leader = False
        self.last_proposed_block = None
        self.last_proposed_received_block = None

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

    def get_worker_shards_latest_commitment(self):
        latest_shards_commitments = {}
        for shard in self.shard.environment[WORKER]:
            block: BlockRivetReference
            for block in self.blockchain[::-1]:
                if shard.id in block.commitments:
                    latest_shards_commitments[shard.id] = {
                        "reference_block_id": block.id,
                        "commitment": block.commitments[shard.id],
                    }

        return latest_shards_commitments

    def extract_crossshard_txs_from_transaction_pool(self):
        not_consumed_transactions = self.transactions_pool[Config.cross_shard_transactions_per_block :]
        consumed_transactions = self.transactions_pool[: Config.cross_shard_transactions_per_block]
        self.transactions_pool = not_consumed_transactions
        return consumed_transactions

    def extract_commitments_from_commitments_pool(self):
        not_consumed_commitments = self.commitments_pool[Config.commitments_per_block :]
        consumed_commitments = self.commitments_pool[: Config.commitments_per_block]
        self.commitments_pool = not_consumed_commitments
        return consumed_commitments

    def reference_receive_new_view_message(self, event: Event):

        if self.current_phase == PREPARE and event.data["current_view_number"] >= self.current_view_number:
            self.new_view_messages += 1
            if self.new_view_messages >= self.shard.get_n_f_value():
                self.is_leader = True

                proposal_block = BlockRivetReference(
                    self.get_blockchain_length(),
                    self.get_last_block(),
                    event.time,
                    self.id,
                    transactions=self.extract_crossshard_txs_from_transaction_pool(),
                    commitments=self.extract_commitments_from_commitments_pool(),
                )

                self.last_proposed_block = proposal_block

                message = {
                    "type": EVT_REFERENCE_RIVET_PREPARE_MESSAGE,
                    "current_view_number": self.current_view_number,
                    "proposal_block": proposal_block
                    # it oculd be necessary to put more details in here
                }
                self.broadcast_message(event, message)

                self.current_phase = PRECOMMIT
                self.reference_create_next_view_interrupt(event)

    def reference_receive_prepare_message(self, event):
        # determine if the PREPARE message should be accepted
        if self.current_phase == PREPARE and event.data["current_view_number"] >= self.current_view_number:
            self.last_proposed_received_block = event.data["proposal_block"]
            Queue.add_event(
                Event(
                    EVT_REFERENCE_RIVET_MESSAGE,
                    self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                    event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
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
                    event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
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
                    event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
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

                self.blockchain.append(self.last_proposed_block)

                self.reference_reset_bookeeping_variables()
                self.reference_create_next_view_interrupt(event)

                self.current_view_number += 1

                if (self.current_view_number % self.shard.n_value) != self.view_number:
                    Queue.add_event(
                        Event(
                            EVT_REFERENCE_RIVET_MESSAGE,
                            self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                            event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
                            {
                                "type": EVT_REFERENCE_RIVET_NEW_VIEW_MESSAGE,
                                "current_view_number": self.current_view_number,
                            },
                        )
                    )

    def reference_receive_decide_message(self, event):

        if self.current_phase == DECIDE and event.data["current_view_number"] >= self.current_view_number:

            self.blockchain.append(self.last_proposed_received_block)
            self.reference_reset_bookeeping_variables()
            self.reference_create_next_view_interrupt(event)

            self.current_view_number += 1

            if (self.current_view_number % self.shard.n_value) != self.view_number:
                Queue.add_event(
                    Event(
                        EVT_REFERENCE_RIVET_MESSAGE,
                        self.shard.view_id_map[self.current_view_number % self.shard.n_value],
                        event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
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
                        event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
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
                    "type": event.data["parent_event"].data["type"],
                    "current_view_number": event.data["current_view_number"],
                },
            )
        )

    def reference_receive_commit_block_state(self, event: Event):
        print(event)
        self.commitments_pool.append(
            {"shard_id": event.data["shard_id"], "block_id": event.data["block_id"], "state": event.data["state"]}
        )

    # worker helper functions

    def request_reference_data(self, event):
        neighbor: NodeL2Rivet
        for neighbor in self.crossshard_neighbors:
            if neighbor.is_leader:
                Queue.add_event(
                    Event(
                        EVT_REFERENCE_RIVET_MESSAGE,
                        neighbor.id,
                        event.time + DelayModel.exponential_delay(WORKER_REFERENCE_COMM_DELAY),
                        {
                            "type": EVT_REFERENCE_RIVET_DATA_REQUEST,
                            "parent_event": event,
                            "current_view_number": self.current_view_number,
                        },
                    )
                )

    def find_reference_leader(self):
        if self.crossshard_neighbors:
            cross_shard_neighbor: NodeL2Rivet
            for cross_shard_neighbor in self.crossshard_neighbors:
                if cross_shard_neighbor.is_leader:
                    return cross_shard_neighbor
            return self.crossshard_neighbors[0]
        else:
            raise Exception("No cross shard neighbors")

    def extract_intrashard_txs_from_transaction_pool(self):
        not_consumed_transactions = self.transactions_pool[Config.transactions_per_block :]
        consumed_transactions = self.transactions_pool[: Config.transactions_per_block]
        self.transactions_pool = not_consumed_transactions
        return consumed_transactions

    def get_latest_committed_worker_block(self):
        last_commitment = {}
        remote_leader: NodeL2Rivet = self.find_reference_leader()
        block: BlockRivetReference

        for block in remote_leader.blockchain[::-1]:
            if self.shard.id in block.commitments:
                last_commitment = block.commitments[self.shard.id]

        if not last_commitment:
            return self.get_last_block()
        else:
            block: BlockRivetWorker
            for block in self.blockchain[::-1]:
                # commitments should have
                # block_id
                # state
                if block.id == last_commitment["block_id"]:
                    return block

    def get_latest_committed_block_reference_block(self):
        remote_leader: NodeL2Rivet = self.find_reference_leader()
        block: BlockRivetReference

        for block in remote_leader.blockchain[::-1]:
            if self.shard.id in block.commitments:
                return block

        return remote_leader.get_last_block()

    def get_cross_shard_transactions_between_reference_blocks(self, p_i: BlockRivetReference, p_j: BlockRivetReference):
        remote_leader: NodeL2Rivet = self.find_reference_leader()

        block: BlockRivetReference

        cross_shard_transactions = []

        for block in remote_leader.blockchain[p_i.height - 1 : p_j.height]:
            transaction: TransactionRivetCrossShard
            for transaction in block.transactions:
                if transaction.sender in self.shard.account_set or transaction.receiver in self.shard.account_set:
                    cross_shard_transactions.append(transaction)

        return cross_shard_transactions

    def get_intrashard_transactions_between_blocks(self, b_i: BlockRivetWorker, b_j: BlockRivetWorker):
        block: BlockRivetWorker
        intra_shard_transactions: list[Transaction] = []
        for block in self.blockchain[b_j.height - 1 : b_j.height]:
            intra_shard_transactions += block.transactions

        return intra_shard_transactions

    def get_latest_reference_block(self):
        remote_leader: NodeL2Rivet = self.find_reference_leader()
        return remote_leader.get_last_block()

    def generate_worker_block(self, timestamp, node_id, block_transactions):
        self.blockchain.append(
            BlockRivetWorker(
                height=self.get_blockchain_length() + 1,
                previous=None,
                timestamp=timestamp,
                minter=node_id,
                state={},
                transactions=block_transactions,
            )
        )

    def uncommit_invalidated_blocks(self, parent_block: BlockRivetWorker):

        while self.get_last_block() != parent_block.id:
            self.blockchain.pop()

    def execute_intra_shard_transactions(self, parent_block_state: dict, intra_shard_transactions=[]):
        new_state = parent_block_state.copy()

        transaction: Transaction
        for transaction in intra_shard_transactions:
            if transaction.sender in new_state:
                new_state[transaction.sender] -= transaction.amount
            else:
                new_state[transaction.sender] = 0
            if transaction.receiver in new_state:
                new_state[transaction.receiver] += transaction.amount
            else:
                new_state[transaction.receiver] = 0
        return new_state

    def execute_cross_shard_transactions(self, parent_block_state: dict, cross_shard_transactions=[]):

        new_state = parent_block_state.copy()

        transaction: TransactionRivetCrossShard
        for transaction in cross_shard_transactions:
            if transaction.sender in self.shard.account_set:
                new_state[transaction.sender] -= transaction.amount

            if transaction.receiver in self.shard.account_set:
                new_state[transaction.receiver] += transaction.amount

        return new_state

    def worker_receive_proposal_message(self, event: Event):

        if self.current_phase == CERTIFICATION and event.data["current_view_number"] >= self.current_view_number:

            #testing behavior
            self.current_view_number = event.data["current_view_number"]

            # create request event
            if not self.waiting_for_data:
                self.waiting_for_data = True
                self.request_reference_data(event)

            b_i: BlockRivetWorker = self.get_latest_committed_worker_block()
            p_i: BlockRivetReference = self.get_latest_committed_block_reference_block()

            b_j: BlockRivetWorker = self.get_last_block()
            p_j: BlockRivetReference = self.get_latest_reference_block()

            q_i_j = self.get_cross_shard_transactions_between_reference_blocks(p_i, p_j)
            t_i_j = self.get_intrashard_transactions_between_blocks(b_i, b_j)

            t_j_plus_1 = self.extract_intrashard_txs_from_transaction_pool()

            if q_i_j:

                self.uncommit_invalidated_blocks(b_i)
                new_state = self.execute_cross_shard_transactions(b_i, q_i_j)
                new_state = self.execute_intra_shard_transactions(new_state, t_i_j + t_j_plus_1)
                b_j_1 = BlockRivetWorker(
                    height=self.get_blockchain_length() + 1,
                    previous=self.get_last_block().hash,
                    timestamp=event.time,
                    minter=self.id,
                    state=new_state,
                    transactions=t_i_j + t_j_plus_1,
                    latest_known_ref_block_height=b_j.height,
                )

            else:
                new_state = self.execute_intra_shard_transactions(b_j.state, t_i_j + t_j_plus_1)
                b_j_1 = BlockRivetWorker(
                    height=self.get_blockchain_length() + 1,
                    previous=self.get_last_block().hash,
                    timestamp=event.time,
                    minter=self.id,
                    state=new_state,
                    transactions=t_i_j + t_j_plus_1,
                )

            self.broadcast_message(
                event,
                {
                    "type": EVT_WORKER_RIVET_CERTIFICATION_MESSAGE,
                    "proposal": b_j_1,
                    "current_view_number": self.current_view_number,
                },
            )

            self.waiting_for_data = False
            self.last_proposed_block = b_j_1
            self.current_phase = PROPOSAL

    def worker_receive_certification_message(self, event):
        # algorithm 4 - might not be necessary
        if self.current_phase == CERTIFICATION and event.data["current_view_number"] >= self.current_view_number:

            # print("view_id_map: "+ str(self.shard.view_id_map))

            Queue.add_event(
                Event(
                    EVT_REFERENCE_RIVET_MESSAGE,
                    self.shard.view_id_map_lookup(self.current_view_number),
                    event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
                    {
                        "type": EVT_WORKER_RIVET_CERTIFICATION_VOTE_MESSAGE,
                        "current_view_number": self.current_view_number,
                    },
                )
            )

            self.blockchain.append(event.data["proposal"])

            self.current_view_number += 1

    def worker_receive_certification_vote_message(self, event):
        # vote if the PROPOSE message should be accepted

        if self.current_phase == PROPOSAL and event.data["current_view_number"] >= self.current_view_number:
            self.certification_votes += 1
            if self.certification_votes >= self.shard.get_f_1_value():
                # block was approved so it should be added to blockchain
                # print("Im receiving enough votes")
                self.blockchain.append(self.last_proposed_block)
                # do commit
                Queue.add_event(
                    Event(
                        EVT_REFERENCE_RIVET_MESSAGE,
                        self.find_reference_leader().id,
                        event.time + DelayModel.exponential_delay(WORKER_REFERENCE_COMM_DELAY),
                        {
                            "type": EVT_REFERENCE_COMMIT_BLOCK_STATE,
                            "shard_id": self.shard.id,
                            "block_id": self.last_proposed_block.id,
                            "state": self.last_proposed_block.state,
                            "transactions": self.last_proposed_block.transactions,
                        },
                    )
                )

                # print("next proposal after commit")
                # schedule next proposal phase

                Queue.add_event(
                    Event(
                        EVT_REFERENCE_RIVET_MESSAGE,
                        self.shard.view_id_map_lookup(self.current_view_number + 1),
                        event.time + DelayModel.exponential_delay(INTRA_SHARD_DELAY),
                        {
                            "type": EVT_WORKER_RIVET_PROPOSAL_MESSAGE,
                            "current_view_number": self.current_view_number+1,
                        },
                    )
                )

                self.current_view_number += 1
                self.current_phase = CERTIFICATION

import uuid
from new_shard_sim.Constants import BLOCK_CREATION_INTERVAL, BLOCK_SIZE, EVT_CREATE_BLOCK, HANDLER_CREATE_BLOCK


from new_shard_sim.Event import Event
from new_shard_sim.Topology import Topology
from new_shard_sim.Transaction import Transaction
from new_shard_sim.Block import Block
from new_shard_sim.Queue import Queue
from new_shard_sim.ComunicationDelay import ComunicationDelay
from new_shard_sim.Blockchain import Blockchain


class Shard:
    def __init__(self, **kwargs):
        self.id = kwargs["id"] if "id" in kwargs else str(uuid.uuid4())
        self.block_size = kwargs["block_size"] if "block_size" in kwargs else BLOCK_SIZE
        self.block_size_child_block = kwargs["block_size_child_block"] if "block_size_child_block" in kwargs else 5
        self.block_creation_interval = (
            kwargs["block_creation_interval"] if "block_creation_interval" in kwargs else BLOCK_CREATION_INTERVAL
        )
        self.name = kwargs["name"] if "name" in kwargs else "default"
        self.blockchain = Blockchain(self.id)
        self.transaction_pool = []
        self.child_block_pool = []

        self.last_known_parent_blockchain_height = 1
        self.last_commited_block = None
        self.blocks_that_caused_penalty = {}

        self.parent: Shard = None
        self.children = []
        self.depth = 1

        self.schedule_kickoff_events()

    def receive_transaction(self, event):
        # add transaction to transaction pool
        transaction: Transaction = event.payload
        self.transaction_pool += [transaction]

    def create_block(self, event):
        # add a certain amount of transactions from the transaction pool to a block
        # and add the block to the block chain
        block = Block(
            height=self.blockchain.get_blockchain_height() + 1,
            shard_id=self.id,
            shard_name=self.name,
            previous_block_hash="H4SH",
            timestamp=event.time,
            transactions=self._consume_transactions_from_pool(),
            child_blocks=self._consume_child_blocks_from_pool(),
        )
        self.blockchain.add_block(block)
        if self.parent != None:
            self.commit_block(block)
        Queue.add_event(
            Event(
                EVT_CREATE_BLOCK,
                self.id,
                event.time + self.block_creation_interval,
                "",
                HANDLER_CREATE_BLOCK,
            )
        )

    def _consume_transactions_from_pool(self):
        if len(self.transaction_pool) > 0:
            if len(self.transaction_pool) > self.block_size:
                remainder_transactions = self.transaction_pool[self.block_size :]
                consumed_transactions = self.transaction_pool[: self.block_size]
                self.transaction_pool = remainder_transactions
                return consumed_transactions
            else:
                consumed_transactions = self.transaction_pool
                self.transaction_pool = []
                return consumed_transactions
        else:
            return self.transaction_pool

    def _consume_child_blocks_from_pool(self):
        if len(self.child_block_pool) > 0:
            if len(self.child_block_pool) > self.block_size_child_block:
                remainder_blocks = self.child_block_pool[self.block_size_child_block :]
                consumed_blocks = self.child_block_pool[: self.block_size_child_block]
                self.child_block_pool = remainder_blocks
                return consumed_blocks
            else:
                consumed_blocks = self.child_block_pool
                self.child_block_pool = []
                return consumed_blocks
        else:
            return self.child_block_pool

    def poll_parent():
        # query parent to see if it has transactions of interest in it's latest blocks
        pass

    def define_parent(self, parent):
        self.parent = parent
        self.depth = parent.depth + 1
        self._subscribe_to_parent(parent)

    def _subscribe_to_parent(self, parent_shard):
        parent_shard.children.append(self)

    def add_block_to_child_block_pool(self, block):
        self.child_block_pool.append(block)

    def rewind_blockchain(self, height):
        removed_blocks = self.blockchain.trim_blockchain(height)
        if self.children:
            self.propagate_penalty_to_children(removed_blocks)

    def propagate_penalty_to_children(self, removed_blocks: Block):
        # shard_id -> smallest height found
        child_block_index = {}
        for block in removed_blocks:
            for child_block in block.child_blocks:
                if child_block.shard_id in child_block_index:
                    if child_block.height < child_block_index[child_block.shard_id]:
                        child_block_index[child_block.shard_id] = child_block.height
                else:
                    child_block_index[child_block.shard_id] = child_block.height

        for child in self.children:
            child.rewind_blockchain(child_block_index[child.id])

    def send_transactions_back_to_transactions_pool(self, blocks):
        for block in blocks:
            self.transaction_pool += block.transactions

    def commit_block(self, block):
        self.last_commited_block = self.blockchain.get_last_commited_block()

        if self.last_commited_block:

            blocks_after_last_commited_block = self.parent.blockchain.get_latest_blocks(self.last_commited_block.height)

            for block in blocks_after_last_commited_block:
                for transaction in block.transactions:
                    if (
                        Topology.address_map[transaction.sender] == self.id
                        or Topology.address_map[transaction.recipient] == self.id
                    ) and block.id not in self.blocks_that_caused_penalty.keys():
                        # maybe it is not necessary to retrieve conflicting transaction
                        # given that the intent of the testing tool is to measure performance
                        # and the performance penalty would already be reflected by removing blocks
                        # from the blockchain
                        self.blocks_that_caused_penalty[block.id] = block

                        blocks_to_remove = self.blockchain.trim_blockchain(self.last_commited_block.height)

                        self.send_transactions_back_to_transactions_pool(blocks_to_remove)
                        return

        self.parent.add_block_to_child_block_pool(block)

    def schedule_kickoff_events(self):
        Queue.add_event(
            Event(EVT_CREATE_BLOCK, self.id, ComunicationDelay.exponential_delay(), "", HANDLER_CREATE_BLOCK)
        )

    def get_current_blockchain_height(self):
        return len(self.blockchain)

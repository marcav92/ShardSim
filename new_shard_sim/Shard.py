import uuid
from new_shard_sim.Constants import (
    BLOCK_CREATION_INTERVAL,
    BLOCK_SIZE,
    CHILD_BLOCKS_PER_BLOCK,
    EVT_CREATE_BLOCK,
    HANDLER_CREATE_BLOCK,
)


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
        self.block_size_child_block = (
            kwargs["block_size_child_block"] if "block_size_child_block" in kwargs else CHILD_BLOCKS_PER_BLOCK
        )
        self.block_creation_interval = (
            kwargs["block_creation_interval"] if "block_creation_interval" in kwargs else BLOCK_CREATION_INTERVAL
        )
        self.name = kwargs["name"] if "name" in kwargs else "default"
        self.blockchain = Blockchain(self.id)
        self.transaction_pool = []
        self.child_block_pool = []

        self.last_known_parent_blockchain_height = 1
        self.last_commited_block = None
        self.addresses_to_skip_in_next_block = []
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

        # print(f"I {self.name} created block with {len(block.transactions)} txs and height {block.height}")
        # print(f"I {self.name} created block with child blocks {block.child_blocks}")
        self.blockchain.add_block(block)
        # self.addresses_to_skip_in_next_block = []
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
        # if len(self.transaction_pool) > 0:
        #     if len(self.transaction_pool) > self.block_size:
        #         remainder_transactions = self.transaction_pool[self.block_size :]
        #         consumed_transactions = self.transaction_pool[: self.block_size]
        #         self.transaction_pool = remainder_transactions
        #         return consumed_transactions
        #     else:
        #         consumed_transactions = self.transaction_pool
        #         self.transaction_pool = []
        #         return consumed_transactions
        # else:
        #     return self.transaction_pool
        consumed_transactions = []
        if len(self.transaction_pool) > 0:
            counter = 0
            transaction_pool_len = len(self.transaction_pool)
            while (
                self.transaction_pool
                and len(consumed_transactions) < self.block_size
                and counter < transaction_pool_len
            ):
                counter += 1
                transaction = self.transaction_pool.pop(0)
                if (
                    transaction.sender not in self.addresses_to_skip_in_next_block
                    and transaction.recipient not in self.addresses_to_skip_in_next_block
                ):
                    consumed_transactions.append(transaction)
                else:
                    # print("detected unwanted transaction")
                    self.transaction_pool.append(transaction)

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
        # print(f"propagating penalty to children {self.name}")
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
        # print(f"{self.name}: blocks that caused penalty {len(self.blocks_that_caused_penalty.keys())}")
        if len(self.addresses_to_skip_in_next_block) == 0:
            self.last_commited_block = self.blockchain.get_last_commited_block()

            not_committed_blocks = self.blockchain.get_not_commited_blocks()

            not_committed_transaction_addresses = {}
            for not_committed_block in not_committed_blocks:
                for transaction in not_committed_block.transactions:
                    not_committed_transaction_addresses[transaction.sender] = not_committed_block.height
                    not_committed_transaction_addresses[transaction.recipient] = not_committed_block.height

            if self.last_commited_block:
                last_parent_blocks = self.parent.blockchain.get_latest_blocks(self.last_commited_block.height)
            else:
                last_parent_blocks = self.parent.blockchain.blockchain

            transaction_addresses_present_in_last_parent_blocks = {}

            for last_parent_block in last_parent_blocks:
                for transaction in last_parent_block.transactions:
                    transaction_addresses_present_in_last_parent_blocks[transaction.sender] = last_parent_block.height
                    transaction_addresses_present_in_last_parent_blocks[
                        transaction.recipient
                    ] = last_parent_block.height

            block_height_to_trim = 1000000000000000000
            for not_committed_address in not_committed_transaction_addresses.keys():
                if not_committed_address in transaction_addresses_present_in_last_parent_blocks.keys():
                    if not_committed_transaction_addresses[not_committed_address] < block_height_to_trim:
                        block_height_to_trim = not_committed_transaction_addresses[not_committed_address]

            if block_height_to_trim != 1000000000000000000:
                # print(f"{self.name} trimming blockchain")
                self.addresses_to_skip_in_next_block = transaction_addresses_present_in_last_parent_blocks.keys()
                blocks_to_remove = self.blockchain.trim_blockchain(block_height_to_trim)
                self.send_transactions_back_to_transactions_pool(blocks_to_remove)
            else:
                # print(f"I {self.name} commited block to my parent")
                self.parent.add_block_to_child_block_pool(block)

        else:
            self.addresses_to_skip_in_next_block = []
            self.parent.add_block_to_child_block_pool(block)
        # if self.last_commited_block:

        #     blocks_after_last_commited_block = self.parent.blockchain.get_latest_blocks(self.last_commited_block.height)

        #     for block in blocks_after_last_commited_block:
        #         for transaction in block.transactions:
        #             if (
        #                 transaction.sender in not_committed_transaction_addresses.keys()
        #                 or transaction.recipient in not_committed_transaction_addresses.keys()
        #             ) and block.id not in self.blocks_that_caused_penalty.keys():
        #                 # maybe it is not necessary to retrieve conflicting transaction
        #                 # given that the intent of the testing tool is to measure performance
        #                 # and the performance penalty would already be reflected by removing blocks
        #                 # from the blockchain
        #                 self.blocks_that_caused_penalty[block.id] = block

        #                 print(f"blockchain being trimmed to {self.last_commited_block.height}")
        #                 blocks_to_remove = self.blockchain.trim_blockchain(self.last_commited_block.height)

        #                 self.send_transactions_back_to_transactions_pool(blocks_to_remove)
        #                 return

    def schedule_kickoff_events(self):
        Queue.add_event(
            Event(EVT_CREATE_BLOCK, self.id, ComunicationDelay.exponential_delay(), "", HANDLER_CREATE_BLOCK)
        )

    def get_current_blockchain_height(self):
        return len(self.blockchain)

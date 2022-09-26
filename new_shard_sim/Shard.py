import uuid
from new_shard_sim.Constants import EVT_CREATE_BLOCK, HANDLER_CREATE_BLOCK


from new_shard_sim.Event import Event
from new_shard_sim.Transaction import Transaction
from new_shard_sim.Block import Block
from new_shard_sim.Queue import Queue
from new_shard_sim.ComunicationDelay import ComunicationDelay


class Shard:
    def __init__(self, **kwargs):
        self.id = kwargs["id"] if "id" in kwargs else uuid.uuid4()
        self.block_size = kwargs["block_size"] if "block_size" in kwargs else 100
        self.block_creation_interval = (
            kwargs["block_creation_interval"] if "block_creation_interval" in kwargs else 5000
        )
        self.blockchain = []
        self.transaction_pool = []
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
        self.blockchain.append(
            Block(
                height=len(self.blockchain) + 1,
                shard_id=self.id,
                previous_block_hash="H4SH",
                timestamp=event.time,
                transactions=self._consume_transactions_from_pool(),
            )
        )
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

    def poll_parent():
        # query parent to see if it has transactions of interest in it's latest blocks
        pass

    def define_parent(self, parent):
        self.parent = parent
        self.depth = parent.depth + 1
        self._subscribe_to_parent(parent)

    def _subscribe_to_parent(self, parent_shard):
        parent_shard.children.append(self)

    def commit_block():
        pass

    def schedule_kickoff_events(self):
        Queue.add_event(
            Event(EVT_CREATE_BLOCK, self.id, ComunicationDelay.exponential_delay(), "", HANDLER_CREATE_BLOCK)
        )

    def get_latest_blocks(self, height):
        return self.blockchain[height - 1 :]

    def get_blocks_within_height_range(self, height_1, height_2):
        # height_2-1+1=height_2
        return self.blockchain[height_1 - 1 : height_2]

    def get_current_blockchain_height(self):
        return len(self.blockchain)

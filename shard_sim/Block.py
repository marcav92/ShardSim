import uuid
import json


class Block:
    def __init__(self, height=0, id=None, previous_block_hash=-1, timestamp=0, minter=None, transactions=[]):
        self.height = height
        self.id = id if id else uuid.uuid4()
        self.previous_block_hash = previous_block_hash
        self.timestamp = timestamp

        # who created this block
        self.minter = minter

        self.transactions = transactions or []

    def __repr__(self):
        return f"""
            depth        : {self.height} 
            id           : {self.id}
            previous     : {self.previous_block_hash}
            timestamp    : {self.timestamp}
            miner        : {self.minter}
            transactions : {self.transactions}
        """


class BlockRivetWorker(Block):
    def __init__(
        self,
        height=0,
        previous=-1,
        timestamp=0,
        state={},
        transactions=[],
        id=None,
        minter=None,
    ):
        super().__init__(height, id, previous, timestamp, minter, transactions)

        self.state = state
        self.is_committed = False
        self.hash = hash(self)

    def set_is_committed(self):
        self.is_committed = True

    def __hash__(self):
        return hash(
            (
                self.height,
                self.id,
                self.previous_block_hash,
                self.timestamp,
                self.minter,
                json.dumps(self.state),
                tuple(self.transactions),
            )
        )


class BlockRivetReference(Block):
    def __init__(self, height=0, id=None, previous=-1, timestamp=0, minter=None, transactions=[], commitments={}):
        super().__init__(height, id, previous, timestamp, minter, transactions)
        self.commitments = commitments
        self.hash = hash(self)

    def __hash__(self):
        return hash(
            (
                self.height,
                self.id,
                self.previous_block_hash,
                self.timestamp,
                self.minter,
                tuple(self.transactions),
                json.dumps(self.commitments),
            )
        )

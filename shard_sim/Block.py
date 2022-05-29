import uuid


class Block:
    def __init__(
        self, height=0, id=None, previous_block_hash=-1, timestamp=0, minter=None, state=None, transactions=[]
    ):
        self.height = height
        self.id = id if id else uuid.uuid4()
        self.previous_block_hash = previous_block_hash
        self.timestamp = timestamp

        # who created this block
        self.minter = minter

        self.transactions = transactions or []

        # dict adress -> value
        self.state = {} if None else state
        self.hash = hash(self)

    def __repr__(self):
        return f"""
            depth        : {self.depth} 
            id           : {self.id}
            previous     : {self.previous}
            timestamp    : {self.timestamp}
            miner        : {self.minter}
            transactions : {self.transactions}
        """


class BlockRivetWorker(Block):
    def __init__(
        self,
        height=0,
        id=None,
        previous=-1,
        timestamp=0,
        minter=None,
        state=None,
        transactions=[],
        latest_known_ref_block_height=0,
    ):
        super().__init__(height, id, previous, timestamp, minter, state, transactions)

        # specific rivet implementation
        # 0 is not a height as a genesis block height would be 1
        self.latest_known_ref_block_height = latest_known_ref_block_height
        self.is_committed = False

    def set_is_committed(self):
        self.is_committed = True

    def __hash__(self):
        return hash(
            (
                self.depth,
                self.id,
                self.previous_block_hash,
                self.timestamp,
                self.minter,
                self.transactions,
                self.state,
                self.latest_known_ref_block_height,
            )
        )


class BlockRivetReference(Block):
    def __init__(self, height=0, id=None, previous=-1, timestamp=0, minter=None, state=None, transactions=[]):
        super().__init__(height, id, previous, timestamp, minter, state, transactions)

    def __hash__(self):
        return hash(
            (self.depth, self.id, self.previous_block_hash, self.timestamp, self.minter, self.transactions, self.state)
        )

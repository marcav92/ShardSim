import uuid


class Block:
    def __init__(
        self, height=0, id=None, shard_id=None, previous_block_hash=-1, timestamp=0, transactions=[], child_blocks=None
    ):
        self.height = height
        self.id = id if id else uuid.uuid4()
        self.shard_id = shard_id
        self.previous_block_hash = previous_block_hash
        self.timestamp = timestamp

        self.transactions = transactions or []
        self.child_blocks = child_blocks or []

    def __repr__(self):
        return f"""
            depth        : {self.height} 
            id           : {self.id}
            previous     : {self.previous_block_hash}
            timestamp    : {self.timestamp}
            miner        : {self.minter}
            transactions : {self.transactions}
        """

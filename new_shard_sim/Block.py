import uuid


class Block:
    def __init__(
        self,
        height=0,
        id=None,
        shard_id=None,
        shard_name=None,
        previous_block_hash=-1,
        timestamp=0,
        transactions=[],
        child_blocks=None,
    ):
        self.height = height
        self.id = id if id else uuid.uuid4()
        self.shard_id = shard_id
        self.shard_name = shard_name
        self.previous_block_hash = previous_block_hash
        self.timestamp = timestamp
        self.parent_height = None

        self.transactions = transactions or []
        self.child_blocks = child_blocks or []

    def __repr__(self):
        return f"""
            height        : {self.height} 
            id           : {self.id}
            previous     : {self.previous_block_hash}
            timestamp    : {self.timestamp}
            shard_id     : {self.shard_id}
            shard_name   : {self.shard_name}
            parent_height: {self.parent_height}
            child_blocks : {self.child_blocks}
        """

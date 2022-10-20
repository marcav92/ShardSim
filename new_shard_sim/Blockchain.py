from new_shard_sim.Block import Block


class Blockchain:
    def __init__(self, shard_id):
        self.blockchain = []
        self.add_genesis_block(Block(height=1, shard_id=shard_id, timestamp=0))

    def add_genesis_block(self, block):
        self.blockchain.append(block)

    def add_block(self, block: Block):
        self.blockchain.append(block)
        for child_block in block.child_blocks:
            child_block.parent_height = len(self.blockchain)

    def get_latest_blocks(self, height):
        return self.blockchain[height:]

    def get_blockchain_height(self):
        return len(self.blockchain)

    def get_last_commited_block(self):
        if self.blockchain:
            for block in self.blockchain[::-1]:
                if block.parent_height:
                    return block
        return None

    def get_blocks_within_height_range(self, height_1, height_2):
        # height_2-1+1=height_2
        return self.blockchain[height_1:height_2]

    def trim_blockchain(self, height):
        removed_blocks = self.blockchain[height:]
        self.blockchain = self.blockchain[:height]
        return removed_blocks

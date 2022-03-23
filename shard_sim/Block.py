class Block():

    def __init__(self, depth=0, id=0, previous=-1, timestamp=0,
        miner=None, transactions=[], size=1.0):
        self.depth = depth
        self.id = id
        self.previous = previous
        self.timestamp = timestamp
        self.miner = miner
        self.transactions = transactions or []
        self.size = size

    def __repr__(self):
        return f'''
            depth        : {self.depth} 
            id           : {self.id}
            previous     : {self.previous}
            timestamp    : {self.timestamp}
            miner        : {self.miner}
            transactions : {self.transactions}
        '''
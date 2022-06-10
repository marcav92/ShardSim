import uuid


class Transaction:
    def __init__(self, timestamp, sender, receiver, amount=0, id=None):
        self.timestamp = timestamp
        self.id = id if id else uuid.uuid4()
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __repr__(self):
        return f"""
            id      : {self.id}
            sender  : {self.sender}
            outpus  : {self.receiver}
            amount  : {self.amount}
        """


class TransactionRivetCrossShard(Transaction):
    def __init__(self, timestamp, sender, receiver, id=None, read_write_set={}):
        super().__init__(timestamp, sender, receiver, id)
        self.read_write_set = read_write_set

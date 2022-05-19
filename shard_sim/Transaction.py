import uuid


class Transaction:
    def __init__(self, timestamp, sender, receiver, id=None):
        self.timestamp = timestamp
        self.id = id if id else uuid.uuid4()
        self.sender = sender
        self.receiver = receiver
        self.amount = 0

    def __repr__(self):
        return f"""
            id      : {self.id}
            sender  : {self.sender}
            outpus  : {self.receiver}
            amount  : {self.amount}
        """

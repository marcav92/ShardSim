import uuid


class Transaction:
    def __init__(self, timestamp, sender, recipient, amount=0, id=None):
        self.timestamp = timestamp
        self.id = id if id else uuid.uuid4()
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def __repr__(self):
        return f"""
            id       : {self.id}
            timestamp: {self.timestamp}
            sender   : {self.sender}
            outpus   : {self.recipient}
            amount   : {self.amount}
        """

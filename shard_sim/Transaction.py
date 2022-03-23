class Transaction():
    
    def __init__(self, timestamp, id, inputs, outputs):
        self.timestamp = timestamp
        self.id = id
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self):
        return f'''
            id      : {self.inputs}
            inputs  : {self.inputs}
            outpus  : {self.outputs}
        '''
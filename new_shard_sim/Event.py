import operator
import time
import uuid


class Event(object):

    """Defines the Event
    :param str type: the event type (block creation or block reception)
    :param int node: the id of the node that the event belongs to
    :param float time: the simualtion time in which the event will be executed at
    :param obj data: the event content
    """

    def __init__(self, type, shard_id, time, payload, handler_name, id=None):
        if handler_name == None:
            raise BaseException("hanlder name not provided")

        self.id = id if id else uuid.uuid4()
        self.type = type
        self.shard_id = shard_id
        self.time = time
        self.payload = payload
        self.handler_name = handler_name

    def __repr__(self):
        return f"""
            id  :   {self.id}
            type:   {self.type} 
            shard_id:  {self.shard_id}
            time:   {self.time}
            payload:   {self.payload}
        """

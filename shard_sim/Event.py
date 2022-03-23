import operator
import time
import uuid

class Event(object):

    """ Defines the Event
        :param str type: the event type (block creation or block reception)
        :param int node: the id of the node that the event belongs to
        :param float time: the simualtion time in which the event will be executed at
        :param obj data: the event content
    """
    def __init__(self, type, node, time, data, id=None):
        self.id = id if id else uuid.uuid4()
        self.type = type
        self.node = node
        self.time = time
        self.data = data

    def __repr__(self):
        return f'''
            id  :   {self.id}
            type:   {self.type} 
            node:   {self.node}
        '''
        









import operator


class Queue:
    event_list = []

    def __repr__():
        return f"""
            event_list: {Queue.event_list}
        """

    def add_event(event):
        Queue.event_list += [event]

    def remove_event(event):
        del Queue.event_list[0]

    def get_next_event():
        Queue.event_list.sort(
            key=operator.attrgetter("time"), reverse=False
        )  # sort events -> earliest one first
        return Queue.event_list.pop(0)

    def size():
        return len(Queue.event_list)

    def isEmpty():
        return len(Queue.event_list) == 0

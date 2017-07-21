from gevent.queue import Queue

def tee(queue, n):
    qt = QueueTee(queue, n)
    return qt.get_tees()


class QueueTee:
    def __init__(self, queue, n):
        self.queue = queue
        self.tees = [QueueTeeGetter(queue_tee=self) for _ in range(n)]

    def get_tees(self):
        return self.tees

    def _get(self, calling_getter):
        val = self.queue.get()
        for getter in self.tees:
            if getter is not calling_getter:
                getter._put(val)
        return val


class QueueTeeGetter:
    def __init__(self, queue_tee):
        self.queue_tee = queue_tee
        self.queue = Queue()

    def _put(self, val):
        self.queue.put(val)

    def get(self):
        if len(self.queue) > 0:
            return self.queue.get()
        elif len(self.queue_tee.queue) > 0:
            return self.queue_tee._get(self)
        else:
            raise StopIteration

    def __next__(self):
        return self.get()

    def __iter__(self):
        return self

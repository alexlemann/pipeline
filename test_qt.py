from pipeline.queue import tee
from gevent.queue import Queue

q = Queue()
q.put(1)
q.put(2)
q.put(5)
q.put(5)
q.put('a')

t1, t2, t3 = tee(q, 3)

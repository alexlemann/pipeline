#!/usr/bin/env python
import gevent
from gevent import monkey

monkey.patch_all() # noqa

import random
from functools import reduce

from pipeline import Stage, Filter, Reduce, pipeline
from pipeline.queue import tee


def randomize_pause(func):
    def inner(*args):
        gevent.sleep(random.uniform(.0001, .01))
        return func(*args)
    return inner


def add_ten(x):
    return x+10


def double(x):
    return 2*x


def triple(x):
    return 3*x


def odds(x):
    return x % 2 == 1


def total(x, y):
    return x+y


data = [1, 2, 3, 4, 5, 6]
print(list(map(add_ten, map(double, data))))
dbl = Stage(double, n_workers=2)
ten = Stage(add_ten, n_workers=2)
res = pipeline([dbl, ten], data)
res.join()
print(res.values)
print('----')


data = [1, 2, 3, 4, 5, 6]
print(list(map(double, map(add_ten, data))))
dbl = Stage(double, n_workers=2)
ten = Stage(add_ten, n_workers=2)
res = pipeline([ten, dbl], data)
res.join()
print(res.values)
print('----')

data = [1, 2, 3, 4, 5, 6]
print(list(map(add_ten, map(double, data))))
dbl = Stage(randomize_pause(double), n_workers=2)
ten = Stage(randomize_pause(add_ten), n_workers=2)
res = pipeline([dbl, ten], data)
res.join()
print(res.values)
print('----')

data = [1, 2, 3, 4, 5, 6]
print(list(map(triple, filter(odds, data))))
filt = Filter(odds, n_workers=2)
trip = Stage(triple, n_workers=2)
res = pipeline([filt, trip], data)
res.join()
print(res.values)
print('----')

data = [1, 2, 3, 4, 5, 6]
print(reduce(total, map(triple, data)))
trip = Stage(triple, n_workers=2)
tot = Reduce(total, initial_value=0)
res = pipeline([trip, tot], data)
res.join()
print(res.values)
print('----')


filt = Filter(odds, n_workers=2)
interim_result = pipeline([filt], range(10))
interim_result.join()
t1, t2 = tee(interim_result.out_q, 2)
trip = Stage(triple, n_workers=2)
trip_pipe_result = pipeline([trip], initial_data=t1)
dbl = Stage(double, n_workers=2)
dbl_pipe_result = pipeline([dbl], initial_data=t2)
trip_pipe_result.join()
dbl_pipe_result.join()

print(list(map(triple, filter(odds, range(10)))))
print(trip_pipe_result.values)
print(list(map(double, filter(odds, range(10)))))
print(dbl_pipe_result.values)
print('----')

data = [1, 2, 3, 4, 5]
range_stage = Stage(range, n_workers=2)
list_stage = Stage(list, n_workers=2, returns_many=True)
res = pipeline([range_stage, list_stage], data)
res.join()
print(res.values)
print('----')

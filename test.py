#!/usr/bin/env python
from pipeline import Stage, Filter, Reduce, pipeline

import random
import gevent


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
dbl = Stage(double, n_workers=2)
ten = Stage(add_ten, n_workers=2)
res = pipeline([dbl, ten], data)
print(res)
print(list(map(add_ten, map(double, data))))
print('----')

data = [1, 2, 3, 4, 5, 6]
dbl = Stage(double, n_workers=2)
ten = Stage(add_ten, n_workers=2)
res = pipeline([ten, dbl], data)
print(res)
print(list(map(double, map(add_ten, data))))
print('----')

data = [1, 2, 3, 4, 5, 6]
dbl = Stage(randomize_pause(double), n_workers=2)
ten = Stage(randomize_pause(add_ten), n_workers=2)
res = pipeline([dbl, ten], data)
print(res)
print(list(map(add_ten, map(double, data))))
print('----')

data = [1, 2, 3, 4, 5, 6]
filt = Filter(odds, n_workers=2)
trip = Stage(triple, n_workers=2)
res = pipeline([filt, trip], data)
print(res)
print(list(map(triple, filter(odds, data))))
print('----')

from functools import reduce
data = [1, 2, 3, 4, 5, 6]
trip = Stage(triple, n_workers=2)
tot = Reduce(total, initial_value=0)
res = pipeline([trip, tot], data)
print(res)
print(reduce(total, map(triple, data)))

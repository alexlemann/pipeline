#!/usr/bin/env python
import unittest

import gevent

import random
from functools import reduce

from pipeline import Stage, Filter, Reduce, pipeline


def randomize_pause(func):
    def inner(*args):
        gevent.sleep(random.uniform(.0001, .01))
        return func(*args)
    return inner


def partition(size):
    def inner(x, y):
        if x is None or not x:
            return [[y]]
        current = x.pop()
        if len(current) == size:
            x.append(current)
            x.append([y])
        else:
            current.append(y)
            x.append(current)
        return x
    return inner


class TestPipeline(unittest.TestCase):

    def setUp(self):
        self.func_double = lambda x: x*2
        self.func_add_ten = lambda x: x+10
        self.func_total = lambda x, y: x+y
        self.func_evens = lambda x: x % 2 == 0

    def test_stage_order_1(self):
        data = [1, 2, 3, 4, 5, 6]
        non_pipeline = list(map(self.func_add_ten, map(self.func_double, data)))
        res = pipeline([
                       Stage(self.func_double, n_workers=2),
                       Stage(self.func_add_ten, n_workers=2),
                       ],
                       initial_data=data)
        res.join()
        self.assertEqual(non_pipeline, [12, 14, 16, 18, 20, 22])
        self.assertEqual(res.values, non_pipeline)

    def test_stage_order_2(self):
        # reverses function order from test_stage_order_1
        data = [1, 2, 3, 4, 5, 6]
        non_pipeline = list(map(self.func_double, map(self.func_add_ten, data)))
        res = pipeline([
                       Stage(self.func_add_ten, n_workers=2),
                       Stage(self.func_double, n_workers=2),
                       ],
                       initial_data=data)
        res.join()
        self.assertEqual(non_pipeline, [22, 24, 26, 28, 30, 32])
        self.assertEqual(res.values, non_pipeline)

    def test_async_unordered(self):
        data = [1, 2, 3, 4, 5, 6]
        non_pipeline = list(map(self.func_double, map(self.func_add_ten, data)))
        res = pipeline([
                       Stage(randomize_pause(self.func_add_ten), n_workers=10),
                       Stage(randomize_pause(self.func_double), n_workers=10),
                       ],
                       initial_data=data)
        res.join()
        values = res.values
        self.assertNotEqual(values, non_pipeline)
        for x in values:
            self.assertIn(x, non_pipeline)

    def test_reduce(self):
        data = [1, 2, 3, 4, 5, 6]
        non_pipeline = reduce(self.func_total, map(self.func_double, data))
        res = pipeline([
                       Stage(self.func_double, n_workers=2),
                       Reduce(self.func_total, initial_value=0),
                       ],
                       initial_data=data).join()
        values = res.values
        self.assertNotEqual(values, non_pipeline)

    def test_partition(self):
        res = pipeline([
                       Stage(self.func_double),
                       Reduce(partition(size=3), initial_value=None),
                       ],
                       initial_data=range(5)
                       ).join()
        values = res.values
        self.assertEqual(values, [[[0, 2, 6], [4, 8]], [[0, 2, 6], [4, 8]], [[0, 2, 6], [4, 8]]])

    def test_filter(self):
        data = range(15)
        non_pipeline = list(filter(self.func_evens, map(self.func_double, data)))
        data = range(15)
        res = pipeline([
                       Stage(self.func_double),
                       Filter(self.func_evens),
                       ],
                       initial_data=data
                       ).join()
        values = res.values
        self.assertEqual(sorted(values), non_pipeline)

if __name__ == '__main__':
    unittest.main()

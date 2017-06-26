#!/usr/bin/env python
import sys

from pipeline import pipeline, Stage


def integerify(x, *args):
    return int(x)

inter = Stage(integerify, n_workers=2)
triple = Stage(lambda x: 3*x, n_workers=2)
res = pipeline([inter, triple], sys.stdin)
print(res)
print('----')

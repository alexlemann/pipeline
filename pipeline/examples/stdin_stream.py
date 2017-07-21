#!/usr/bin/env python
""" **stdin_stream** is a realtime example of using a generator as initial data.
This is interesting because it demonstrates how the pipeline can operate not
only on lists of predefined objects, but also on generators of new data that is
being created in realtime.
"""
import sys

from pipeline import pipeline, Stage
import gevent

from gevent import monkey
monkey.patch_all() # noqa


def integerify(x):
    try:
        return int(x)
    except:
        return None


def triple(x):
    try:
        return 3*x
    except:
        return None

if __name__ == "__main__":
    integerify_stage = Stage(integerify, n_workers=2)
    triple_stage = Stage(triple, n_workers=2)
    print(pipeline([integerify_stage, triple_stage], sys.stdin).join().values)
    p = pipeline([integerify_stage, triple_stage], sys.stdin)
    for x in p.out_q:
        print(x)
    p = pipeline([integerify_stage, triple_stage], sys.stdin)
    while 1:
        sys.stdin.flush()
        p = pipeline([integerify_stage, triple_stage], sys.stdin)
        if p.out_q:
            print(p.out_q.get())
        gevent.sleep(0)

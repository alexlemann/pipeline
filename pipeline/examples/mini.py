#!/bin/env python
"""Our first example is a Pipeline with two Stages.

1. Stage 1 is the `fizz buzz <https://wikipedia.org/wiki/fizzbuzz>`_ algorithm.  Taking a number and returning a pair that indicates the original number and the resultant string of 'fizz', 'buzz', 'fizzbuzz' or an empty string, ''.
2. The second Stage takes tuples of integers and their fizzbuzz string and applies an uppercase operation to the string portion of the tuple. A new tuple of the integer and an all uppercase fizzbuzz string.

=========== = ======== = =========
pipeline
----------------------------------
1) fizzbuzz → 2) upper → 3) result
=========== = ======== = =========


>>> from pipeline import pipeline, Stage
>>> from pipeline.examples.mini import fizzbuzz
>>> # Define a pipeline from two stage functions
>>> fizzbuzz_upper_pipe = pipeline(
...    stages=[
...            Stage(fizzbuzz, n_workers=1),
...            Stage(lambda x: (x[0], str.upper(x[1])) , n_workers=1),
...           ],
...    initial_data=range(1, 16)
... )
>>> # Join workers to wait for final results
>>> fizzbuzz_upper_pipe.join() # doctest: +ELLIPSIS
<pipeline.pipeline.PipelineResult object at 0x...>
>>> sorted(fizzbuzz_upper_pipe.values)
[(1, ''), (2, ''), (3, 'FIZZ'), (4, ''), (5, 'BUZZ'), (6, 'FIZZ'), (7, ''), (8, ''), (9, 'FIZZ'), (10, 'BUZZ'), (11, ''), (12, 'FIZZ'), (13, ''), (14, ''), (15, 'FIZZBUZZ')]
"""
from gevent import monkey
monkey.patch_all()


def fizzbuzz(i):
    """
    :param i: Any integer to be evaluated by the fizzbuzz algorithm
    :return: An (integer, fizzbuzz string) pair that indicates what fizzbuzz
      evaluates to given the integer.
    """
    if i % 3 == 0 and i % 5 == 0:
        return i, 'fizzbuzz'
    elif i % 3 == 0:
        return i, 'fizz'
    elif i % 5 == 0:
        return i, 'buzz'
    return (i, '')


if __name__ == "__main__":
    import doctest
    doctest.testmod()

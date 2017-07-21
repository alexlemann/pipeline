#!/usr/bin/env python3
import logging
import types

from gevent.queue import Queue
from gevent.pool import Pool, Group
import gevent


logger = logging.getLogger(__name__)


class DROP:
    """
    If a Stage function returns DROP, there will be no item added to the input
      queue of the subsequent stage.
    """
    pass


def stage_monitor(stage):
    """
    Stage monitor is a worker that monitors a stage while it is being executed.
      The stage monitor coordinates running stage workers, saving results, and
      determining the end of any particular stage.
    """
    # Pool of stage function worker greenlets.
    work_pool = Pool(size=stage.n_workers)
    # Group of greenlets which save results from workers via callbacks.
    save_group = Group()

    def save_result(x):
        """
        Save results onto the output queue as a tuple or if there is only
          a single returned value, save that instead as that singular item.
        """
        if type(stage) == Reduce:
            # XXX: This would not work for stream inputs afaict
            #   But, reduction should not work anyway
            if len(work_pool) + len(save_group) + len(stage.in_q) == 1:
                stage.out_q.put(x)
        else:
            if not stage.returns_many:
                stage.out_q.put(x)
            else:
                try:
                    for i in x:
                        stage.out_q.put(i)
                except:
                    stage.out_q.put([x])

    for x in stage.in_q:
        """
        Iterate the input queue until StopIteration is received.
          Spawn new workers for work items on the input queue.
          Keep track of storing results via a group of result saving greenlets.

        Ignore all DROP items in the input queue.

        Once we receive a StopIteration, wait for all open workers to finish
          and once they are finished, bubble the StopIteration to the next stage
        """
        gevent.sleep(0)
        if x is DROP:
            continue
        if x is StopIteration:
            break
        func_args = [x]
        cb_worker = work_pool.apply_async(stage.func,
                                          func_args,
                                          callback=save_result)
        save_group.add(cb_worker)
    logger.debug('Worker Pool: << {} >>'.format(work_pool))
    work_pool.join()
    save_group.join()
    stage.out_q.put(StopIteration)
    return stage


def _make_filter(func):
    def inner(x):
        if func(x):
            return x
        else:
            return DROP
    return inner


def _make_reduce(func):
    def inner(y):
        if not hasattr(func, '__accumulator'):
            x = func.initial_value
        else:
            x = func.__accumulator
        func.__accumulator = func(x, y)
        return func.__accumulator
    return inner


class Stage:
    def __init__(self, func, n_workers=1, returns_many=False):
        self.func = func
        self.n_workers = n_workers
        self.returns_many = returns_many


class Reduce(Stage):
    def __init__(self, func, initial_value):
        reduce_func = _make_reduce(func)
        func.initial_value = initial_value
        super(Reduce, self).__init__(reduce_func)


class Filter(Stage):
    """Creates a stage that follows the Python builtin filter function interface
    by dropping any values for which ``filter_function`` does not return
    ``True``.

    This is a helper that creates a wrapper around ``filter_function`` that
    returns a ``DROP`` object when the result is not ``True``

    >>> from pipeline import Filter, Stage, pipeline
    >>> def remove_evens(x):
    ...     return x % 2 == 1
    >>> pr = pipeline(stages=[Filter(remove_evens, n_workers=1),
    ...                       Stage(lambda x: x * 3, n_workers=1)],
    ...               initial_data=[1, 2, 3, 4, 5, 6])
    >>> pr.join() # doctest: +ELLIPSIS
    <....PipelineResult object at 0x...>
    >>> print(pr.values)
    [3, 9, 15]
    """
    def __init__(self, function, n_workers=1):
        filter_function = _make_filter(function)
        super(Filter, self).__init__(filter_function, n_workers)


class PipelineResult:
    def __init__(self, monitors, out_q):
        self.monitors = monitors
        self.out_q = out_q

    def join(self):
        self.monitors.join()
        return self

    @property
    def values(self):
        if len(self.monitors) > 0:
            raise Exception('Pipeline is not finished.'
                            'Use pipeline.join() to wait for completion. '
                            'Or use pipeline.out_q to consume partial results.')
        # Final iteration to drop DROPs and StopIteration
        return list(filter(lambda x: x is not DROP, self.out_q))

    def __iter__(self):
        return self

    def __next__(self):
        while 1:
            x = next(self.out_q)
            if x is StopIteration:
                raise StopIteration
            elif x is DROP:
                continue
            else:
                return x


def pipeline(stages, initial_data):
    monitors = Group()
    # Make sure items in initial_data are iterable.
    if not isinstance(initial_data, types.GeneratorType):
        try:
            iter(initial_data)
        except:
            raise TypeError('initial_data must be iterable')
    # The StopIteration will bubble through the queues as it is reached.
    #   Once a stage monitor sees it, it indicates that the stage will read
    #   no more data and the monitor can wait for the current work to complete
    #   and clean up.
    if hasattr(initial_data, 'append'):
        initial_data.append(StopIteration)
    if not stages:
        return PipelineResult(monitors, [])
    # chain stage queue io
    #  Each stage shares an output queue with the next stage's input.
    qs = [initial_data] + [Queue() for _ in range(len(stages))]
    for stage, in_q, out_q in zip(stages, qs[:-1], qs[1:]):
        stage.in_q = in_q
        stage.out_q = out_q
        monitors.spawn(stage_monitor, stage)
    gevent.sleep(0)
    return PipelineResult(monitors, stages[-1].out_q)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

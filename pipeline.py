import logging

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


def make_filter(func):
    def inner(*args):
        if func(*args):
            return args
        else:
            return DROP
    return inner


def stage_monitor(stage):
    work_pool = Pool(size=stage.n_workers)
    save_group = Group()

    def save_result(*args):
        logger.debug('Saving << {} >>'.format(args))
        if len(args) == 1:
            args = args[0]
        stage.out_q.put(args)

    for x in stage.in_q:
        gevent.sleep(0)
        if x is StopIteration:
            break
        if x is DROP:
            continue
        logger.debug('Spawning << {} >> with << {} >>'.format(stage.func, x))
        try:
            func_args = iter(x)
        except TypeError:
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


class Stage:
    def __init__(self, func, n_workers=1):
        self.func = func
        self.n_workers = n_workers


class Reduce(Stage):
    def __init__(self, func):
        super(Reduce).__init__(func, n_workers=1)


class Filter(Stage):
    def __init__(self, func, n_workers=1):
        filter_func = make_filter(func)
        super(Filter, self).__init__(filter_func, n_workers)


def pipeline(stages, initial_data):
    monitors = Group()
    # Make sure items in initial_data are iterable.
    #  They are considered iterables of func arguments.
    try:
        [iter(x) for x in initial_data]
    except TypeError:
        initial_data = [[x] for x in initial_data]
    # chain stage queue io
    #  Each stage shares an output queue with the next stage's input.
    initial_data.append(StopIteration)
    qs = [initial_data] + [Queue() for _ in range(len(stages))]
    for stage, in_q, out_q in zip(stages, qs[:-1], qs[1:]):
        stage.in_q = in_q
        stage.out_q = out_q
        monitors.spawn(stage_monitor, stage)
        gevent.sleep(0)
    monitors.join()
    # final_output is in a nice format and iterates over the final queue in
    #   order to remove the StopIteration item.
    final_output = list(stages[-1].out_q)
    return final_output

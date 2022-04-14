import ray
import types

from typing import List, Callable
from ray.util.queue import Queue

class StageCompleteSignal: pass

@ray.remote(num_cpus=0)
def ray_stage_wait_and_alert(tasks: ray.ObjectRef, output_queue: Queue):
    ray.get(tasks)
    for q in output_queue:
        q.put(StageCompleteSignal)

@ray.remote
def ray_stage(funcs: List[Callable], input_queue: Queue, output_queue: Queue):
    pfuncs = []
    for f in funcs:
        if hasattr(f, 'prepare'):
            f.prepare()
        pfuncs.append(f)

    if len(input_queue) > 1 or len(output_queue) > 1:
            raise NotImplementedError

    if len(pfuncs) == 0:
        return

    if len(input_queue) == 0:
        # source node
        first = pfuncs[0]()
        if not isinstance(first, types.GeneratorType):
            raise TypeError('The first function in the first stage needs to '
                    + 'return a generator')
        for next_item in first:
            for f in pfuncs[1:]:
                next_item = f(next_item)
            for q in output_queue:
                q.put(next_item)
    else:
        while True:
            next_item = input_queue[0].get(block=True)
            if next_item is StageCompleteSignal:
                input_queue[0].put(StageCompleteSignal)
                break
            for f in pfuncs:
                next_item = f(next_item)
            for q in output_queue:
                q.put(next_item)



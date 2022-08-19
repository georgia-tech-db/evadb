import ray
from typing import List, Callable
from ray.util.queue import Queue


class StageCompleteSignal:
    pass


@ray.remote(num_cpus=0)
def ray_stage_wait_and_alert(tasks: ray.ObjectRef, output_queue: Queue):
    ray.get(tasks)
    for q in output_queue:
        q.put(StageCompleteSignal)


@ray.remote
def ray_stage(
    exectuor: Callable, 
    input_queues: List[Queue],
    output_queues: List[Queue]
):
    if len(input_queues) > 1 or len(output_queues) > 1:
        raise NotImplementedError

    gen = exectuor(input_queues=input_queues)
    for next_item in gen:
        for oq in output_queues:
            oq.put(next_item)

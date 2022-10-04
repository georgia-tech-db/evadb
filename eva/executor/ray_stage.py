# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Callable, List

import ray
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
    exectuor: Callable, input_queues: List[Queue], output_queues: List[Queue]
):
    if len(input_queues) > 1 or len(output_queues) > 1:
        raise NotImplementedError

    gen = exectuor(input_queues=input_queues)
    for next_item in gen:
        for oq in output_queues:
            oq.put(next_item)

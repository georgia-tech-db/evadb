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
from typing import Iterator

from ray.util.queue import Queue

from eva.executor.abstract_executor import AbstractExecutor
from eva.experimental.ray.executor.ray_stage import (
    StageCompleteSignal,
    ray_stage,
    ray_stage_wait_and_alert,
)
from eva.experimental.ray.planner.exchange_plan import ExchangePlan
from eva.models.storage.batch import Batch


class QueueReaderExecutor(AbstractExecutor):
    def __init__(self):
        super().__init__(None)

    def validate(self):
        pass

    def exec(self, **kwargs) -> Iterator[Batch]:
        assert (
            "input_queues" in kwargs
        ), "Invalid ray exectuion stage. No input_queue found"
        input_queues = kwargs["input_queues"]
        assert len(input_queues) == 1, "Not support mulitple input queues yet"
        iq = input_queues[0]

        while True:
            next_item = iq.get(block=True)
            if next_item is StageCompleteSignal:
                iq.put(StageCompleteSignal)
                break
            else:
                yield next_item


class ExchangeExecutor(AbstractExecutor):
    """
    Applies predicates to filter the frames which satisfy the condition
    Arguments:
        node (AbstractPlan): The SequentialScanPlan

    """

    def __init__(self, node: ExchangePlan):
        self.parallelism = node.parallelism
        self.ray_conf = node.ray_conf
        super().__init__(node)

    def validate(self):
        pass

    def exec(self, is_top=True) -> Iterator[Batch]:
        assert (
            len(self.children) == 1
        ), "Exchange executor does not support children != 1"

        # Find the exchange exector below the tree
        curr_exec = self
        input_queues = []
        while len(curr_exec.children) > 0 and not isinstance(
            curr_exec.children[0], ExchangeExecutor
        ):
            curr_exec = curr_exec.children[0]

        if len(curr_exec.children) > 0:
            iq = yield from curr_exec.children[0].exec(is_top=False)
            input_queues.append(iq)
            queue_exec = QueueReaderExecutor()
            curr_exec.children = [queue_exec]

        output_queue = Queue(maxsize=100)
        ray_task = []
        for _ in range(self.parallelism):
            ray_task.append(
                ray_stage.options(**self.ray_conf).remote(
                    self.children[0], input_queues, [output_queue]
                )
            )
        ray_stage_wait_and_alert.remote(ray_task, [output_queue])
        while is_top:
            res = output_queue.get(block=True)
            if res is StageCompleteSignal:
                break
            else:
                yield res
        else:
            return output_queue

    def __call__(self, batch: Batch) -> Batch:
        pass

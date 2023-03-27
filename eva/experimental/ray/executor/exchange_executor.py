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
from eva.executor.executor_utils import ExecutorError
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

        # Index of input queue.
        self.q_idx = None

    def exec(self, **kwargs) -> Iterator[Batch]:
        assert (
            "input_queues" in kwargs
        ), "Invalid ray exectuion stage. No input_queue found"
        input_queues = kwargs["input_queues"]
        iq = input_queues[self.q_idx]

        while True:
            next_item = iq.get(block=True)
            if next_item is StageCompleteSignal:
                iq.put(StageCompleteSignal)
                break
            elif isinstance(next_item, ExecutorError):
                # Raise ExecutorError immediately from queue.
                raise next_item
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

    def _find_all_parent_executor_of_exchange(self, curr_exec):
        # Traverse the query execution tree in a DFS manner. This
        # function will return the parent executor of ExchangeExecutor,
        # which will later be inserted a queue reader.

        # Start with checking if current executor has any child.
        if len(curr_exec.children) > 0:
            # Check if child executor is ExchangeExecutor. If so, return.
            # Otherwise, traverse further down.
            if isinstance(curr_exec.children[0], ExchangeExecutor):
                yield curr_exec
            else:
                for child in curr_exec.children:
                    yield from self._find_all_parent_executor_of_exchange(child)

    def exec(self, is_top=True) -> Iterator[Batch]:
        assert (
            len(self.children) == 1
        ), "Exchange executor does not support children != 1"

        # Find all parent of ExchangeExecutor below current executor.
        # Attach a queue reader to those parent executors.
        input_queues = []
        for parent_exec in self._find_all_parent_executor_of_exchange(self):
            iq = yield from parent_exec.children[0].exec(is_top=False)
            input_queues.append(iq)
            queue_exec = QueueReaderExecutor()
            # Set queue index if an executor has multiple input executors.
            queue_exec.q_idx = len(input_queues) - 1
            parent_exec.children = [queue_exec]

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
            elif isinstance(res, ExecutorError):
                # Raise ExecutorError for the topmost Exchange.
                raise res
            else:
                yield res
        else:
            return output_queue

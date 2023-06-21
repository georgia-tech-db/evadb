# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import ExecutorError
from evadb.executor.ray_utils import (
    StageCompleteSignal,
    ray_parallel,
    ray_pull,
    ray_wait_and_alert,
)
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.exchange_plan import ExchangePlan


class QueueReaderExecutor(AbstractExecutor):
    def __init__(self):
        super().__init__(None, None)

    def exec(self, **kwargs) -> Iterator[Batch]:
        assert "input_queue" in kwargs, "Invalid ray execution. No input_queue found"
        input_queue = kwargs["input_queue"]

        while True:
            next_item = input_queue.get(block=True)
            if next_item is StageCompleteSignal:
                # Stop signal is put back to input queue again
                # to ensure it is propagated to all ray parallel
                # actors.
                input_queue.put(StageCompleteSignal)
                break
            elif isinstance(next_item, ExecutorError):
                input_queue.put(next_item)
                raise next_item
            else:
                yield next_item


class ExchangeExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: ExchangePlan):
        self.inner_plan = node.inner_plan
        self.parallelism = node.parallelism
        self.ray_pull_env_conf_dict = node.ray_pull_env_conf_dict
        self.ray_parallel_env_conf_dict = node.ray_parallel_env_conf_dict
        super().__init__(db, node)

    def build_inner_executor(self, inner_executor):
        self.inner_executor = inner_executor
        self.inner_executor.children = [QueueReaderExecutor()]

    def exec(self) -> Iterator[Batch]:
        from ray.util.queue import Queue

        input_queue = Queue(maxsize=100)
        output_queue = Queue(maxsize=100)

        # Pull data from child executor
        assert (
            len(self.children) == 1
        ), "Exchange currently only supports parallelization of node with only one child"
        ray_pull_task = ray_pull().remote(
            self.ray_pull_env_conf_dict,
            self.children[0],
            input_queue,
        )

        # Parallel the inner executor.
        ray_parallel_task_list = []
        for i in range(self.parallelism):
            ray_parallel_task_list.append(
                ray_parallel().remote(
                    self.ray_parallel_env_conf_dict[i],
                    self.inner_executor,
                    input_queue,
                    output_queue,
                )
            )

        ray_wait_and_alert().remote([ray_pull_task], input_queue)
        ray_wait_and_alert().remote(ray_parallel_task_list, output_queue)

        while True:
            res = output_queue.get(block=True)
            if res is StageCompleteSignal:
                break
            elif isinstance(res, ExecutorError):
                raise res
            else:
                yield res

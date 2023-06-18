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
import os
from typing import Callable, Dict, Iterator

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.exchange_plan import ExchangePlan
from evadb.utils.generic_utils import try_to_import_ray


class QueueReaderExecutor(AbstractExecutor):
    def __init__(self):
        super().__init__(None, None)
        try_to_import_ray()

    def exec(self, **kwargs) -> Iterator[Batch]:
        class StageCompleteSignal:
            pass

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
        try_to_import_ray()
        self.inner_plan = node.inner_plan
        self.parallelism = node.parallelism
        self.ray_pull_env_conf_dict = node.ray_pull_env_conf_dict
        self.ray_parallel_env_conf_dict = node.ray_parallel_env_conf_dict
        super().__init__(db, node)

    # @ray.remote(num_cpus=0)
    def ray_wait_and_alert(tasks, queue):
        class StageCompleteSignal:
            pass

        # tasks : List[ray.ObjectRef]
        import ray
        from ray.exceptions import RayTaskError

        try:
            ray.get(tasks)
            queue.put(StageCompleteSignal)
        except RayTaskError as e:
            queue.put(ExecutorError(e.cause))

    # Max calls set to 1 to forcefully release GPU resource when the job is
    # complete. We choose to bypass resource management of Ray, but instead
    # control GPU resource ourselves by configuring the environmental variables
    # when the job enters the Ray process. Due to that, resource release is not
    # cleanly done on the Ray side, we need to set this to prevent memory leak.
    # More detailed explanation can be found in
    # https://github.com/georgia-tech-db/eva/pull/731
    # @ray.remote(max_calls=1)
    def ray_parallel(
        conf_dict: Dict[str, str],
        executor: Callable,
        input_queue,
        output_queue,
    ):
        for k, v in conf_dict.items():
            os.environ[k] = v

        gen = executor(input_queue=input_queue)
        for next_item in gen:
            output_queue.put(next_item)

    # @ray.remote(max_calls=1)
    def ray_pull(conf_dict: Dict[str, str], executor: Callable, input_queue):
        for k, v in conf_dict.items():
            os.environ[k] = v

        for next_item in executor():
            input_queue.put(next_item)

    def build_inner_executor(self, inner_executor):
        self.inner_executor = inner_executor
        self.inner_executor.children = [QueueReaderExecutor()]

    def exec(self) -> Iterator[Batch]:
        class StageCompleteSignal:
            pass

        try_to_import_ray()
        from ray.util.queue import Queue

        input_queue = Queue(maxsize=100)
        output_queue = Queue(maxsize=100)

        # Pull data from child executor
        assert (
            len(self.children) == 1
        ), "Exchange currently only supports parallelization of node with only one child"
        ray_pull_task = self.ray_pull.remote(
            self.ray_pull_env_conf_dict,
            self.children[0],
            input_queue,
        )

        # Parallel the inner executor.
        ray_parallel_task_list = []
        for i in range(self.parallelism):
            ray_parallel_task_list.append(
                self.ray_parallel.remote(
                    self.ray_parallel_env_conf_dict[i],
                    self.inner_executor,
                    input_queue,
                    output_queue,
                )
            )

        self.ray_wait_and_alert.remote([ray_pull_task], input_queue)
        self.ray_wait_and_alert.remote(ray_parallel_task_list, output_queue)

        while True:
            res = output_queue.get(block=True)
            if res is StageCompleteSignal:
                break
            elif isinstance(res, ExecutorError):
                raise res
            else:
                yield res

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
from collections import deque

from eva.optimizer.optimizer_tasks import OptimizerTask


class OptimizerTaskStack:
    def __init__(self):
        self._task_stack = deque()

    def push(self, task: OptimizerTask):
        self._task_stack.append(task)

    def pop(self) -> OptimizerTask:
        return self._task_stack.pop()

    def empty(self) -> bool:
        return not self._task_stack

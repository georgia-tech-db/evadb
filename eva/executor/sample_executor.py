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

from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.sample_plan import SamplePlan


class SampleExecutor(AbstractExecutor):
    """
    Samples uniformly from the rows.

    Arguments:
        node (AbstractPlan): The Sample Plan

    """

    def __init__(self, node: SamplePlan):
        super().__init__(node)
        self._sample_freq = node.sample_freq.value

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        child_executor = self.children[0]

        current = 0
        for batch in child_executor.exec():
            result_batch = batch[current :: self._sample_freq]
            result_batch.reset_index()
            yield result_batch
            current = (current - len(batch)) % self._sample_freq

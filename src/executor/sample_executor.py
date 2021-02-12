# coding=utf-8
# Copyright 2018-2020 EVA
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

from src.models.storage.batch import Batch
from src.executor.abstract_executor import AbstractExecutor
from src.planner.sample_plan import SamplePlan
from src.configuration.configuration_manager import ConfigurationManager


class SampleExecutor(AbstractExecutor):
    """
    Samples uniformly from the rows.

    Arguments:
        node (AbstractPlan): The Sample Plan

    """

    def __init__(self, node: SamplePlan):
        super().__init__(node)
        self._sample_freq = node.sample_value
        self.BATCH_MAX_SIZE = ConfigurationManager().get_value(
            "executor", "batch_size")

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        child_executor = self.children[0]
        # aggregates the batches into one large batch
        current = 0
        for batch in child_executor.exec():
            start = current
            for i in range(start, len(batch), self._sample_freq):
                yield batch[i:i + 1]
            current = (current - len(batch)) % self._sample_freq

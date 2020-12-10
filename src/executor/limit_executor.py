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
from src.planner.limit_plan import LimitPlan
from src.utils.logging_manager import LoggingManager, LoggingLevel


class LimitExecutor(AbstractExecutor):
    """
    Limits the number of rows returned

    Arguments:
        node (AbstractPlan): The Limit Plan

    """

    def __init__(self, node: LimitPlan):
        super().__init__(node)
        self._limit_count = node.limit_value
        self.BATCH_MAX_SIZE = 50  # from eva.yml

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        child_executor = self.children[0]
        aggregated_batch_list = []

        # aggregates the batches into one large batch
        for batch in child_executor.exec():
            aggregated_batch_list.append(batch)
        aggregated_batch = Batch.concat(aggregated_batch_list, copy=False)

        aggregated_frame = aggregated_batch.frames

        # limits the rows
        if self._limit_count <= aggregated_frame.shape[0]:
            aggregated_frame = aggregated_frame.iloc[:self._limit_count]
        else:
            LoggingManager().log('Limit value greater than \
                    current size of data!', LoggingLevel.WARNING)

        # split the aggregated batch into smaller ones based
        #  on self.BATCH_MAX_SIZE
        for i in range(0, aggregated_frame.shape[0], self.BATCH_MAX_SIZE):
            bound = i + self.BATCH_MAX_SIZE
            if bound > aggregated_frame.shape[0]:
                bound = aggregated_frame.shape[0]
            batch = Batch(frames=aggregated_frame.iloc[i: bound])
            batch.reset_index()
            yield batch

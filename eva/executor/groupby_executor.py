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

import pandas as pd

from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.groupby_plan import GroupByPlan


class GroupByExecutor(AbstractExecutor):
    """
    Group inputs into 4d segments of length provided in the query
    E.g., "GROUP BY '8f'" groups every 8 frames into one segment

    Arguments:
        node (AbstractPlan): The GroupBy Plan

    """

    def __init__(self, node: GroupByPlan):
        super().__init__(node)
        self._segment_length = int(node.groupby_clause.value[:-1])

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        child_executor = self.children[0]

        buffer = Batch(pd.DataFrame())
        for batch in child_executor.exec():
            new_batch = buffer + batch
            # We assume that all the segments exactly of segment_length size
            # and discard any dangling frames in the end.
            while len(new_batch) >= self._segment_length:
                yield new_batch[: self._segment_length]
                new_batch = new_batch[self._segment_length :]
            buffer = new_batch

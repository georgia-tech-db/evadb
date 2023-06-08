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
import re
from typing import Iterator

import pandas as pd

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.groupby_plan import GroupByPlan


class GroupByExecutor(AbstractExecutor):
    """
    Group inputs into 4d segments of length provided in the query
    E.g., "GROUP BY '8 frames'" groups every 8 frames into one segment

    Arguments:
        node (AbstractPlan): The GroupBy Plan

    """

    def __init__(self, db: EvaDBDatabase, node: GroupByPlan):
        super().__init__(db, node)
        numbers_only = re.sub(r"\D", "", node.groupby_clause.value)
        self._segment_length = int(numbers_only)

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]

        buffer = Batch(pd.DataFrame())
        for batch in child_executor.exec(**kwargs):
            new_batch = buffer + batch
            # We assume that all the segments exactly of segment_length size
            # and discard any dangling frames in the end.
            while len(new_batch) >= self._segment_length:
                yield new_batch[: self._segment_length]
                new_batch = new_batch[self._segment_length :]
            buffer = new_batch

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
import re
import pandas as pd

from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.groupby_plan import GroupByPlan
from eva.utils.logging_manager import logger

class GroupByExecutor(AbstractExecutor):
    """
    Samples uniformly from the rows.

    Arguments:
        node (AbstractPlan): The Sample Plan

    """

    def __init__(self, node: GroupByPlan):
        super().__init__(node)
        # match the pattern of group by clause (e.g., 16f or 8s)
        pattern = re.search(r'^\d+[fs]$', node.groupby_clause.value)
        # if valid pattern
        if pattern:
            match_string = pattern.group(0)
            if match_string[-1] == 'f':
                self._segment_length = int(match_string[:-1])
                # TODO ACTION condition on segment length?
            else:
                err_msg = "Only grouping by frames (f) is supported"
                logger.exception(err_msg)
        else:
            err_msg = "Incorrect GROUP BY pattern: {}".format(node.groupby_clause.value)
            logger.exception(err_msg)

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        child_executor = self.children[0]

        buffer = Batch(pd.DataFrame())
        for batch in child_executor.exec():
            new_batch = buffer + batch
            while len(new_batch) >= self._segment_length:
                yield new_batch[:self._segment_length]
                new_batch = new_batch[self._segment_length:]
            buffer = new_batch

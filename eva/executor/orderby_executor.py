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
from eva.parser.types import ParserOrderBySortType
from eva.planner.orderby_plan import OrderByPlan


class OrderByExecutor(AbstractExecutor):
    """
    Sort the frames which satisfy the condition

    Arguments:
        node (AbstractPlan): The OrderBy Plan

    """

    def __init__(self, node: OrderByPlan):
        super().__init__(node)
        self._orderby_list = node.orderby_list
        self._columns = node.columns
        self._sort_types = node.sort_types
        self.batch_sizes = []

    def validate(self):
        pass

    def extract_column_names(self):
        """extracts the string name of the column"""
        # self._columns: List[TupleValueExpression]
        return [tve.col_alias for tve in self._columns]

    def extract_sort_types(self):
        """extracts the sort type for the column"""
        # self._sort_types: List[ParserOrderBySortType]
        sort_type_bools = []
        for st in self._sort_types:
            if st is ParserOrderBySortType.ASC:
                sort_type_bools.append(True)
            else:
                sort_type_bools.append(False)
        return sort_type_bools

    def exec(self) -> Iterator[Batch]:
        child_executor = self.children[0]
        aggregated_batch_list = []

        # aggregates the batches into one large batch
        for batch in child_executor.exec():
            self.batch_sizes.append(len(batch))
            aggregated_batch_list.append(batch)
        aggregated_batch = Batch.concat(aggregated_batch_list, copy=False)

        # sorts the batch
        try:
            aggregated_batch.sort_orderby(
                by=self.extract_column_names(),
                sort_type=self.extract_sort_types(),
            )
        except KeyError:
            # pass for now
            pass

        # split the aggregated batch into smaller ones based
        #  on self.batch_sizes which holds the input batches sizes
        index = 0
        for i in self.batch_sizes:
            batch = aggregated_batch[index : index + i]
            batch.reset_index()
            index += i
            yield batch

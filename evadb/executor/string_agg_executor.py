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
from evadb.expression.function_expression import FunctionExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.models.storage.batch import Batch
from evadb.parser.types import ParserOrderBySortType
from evadb.plan_nodes.orderby_plan import OrderByPlan
from evadb.plan_nodes.string_agg_plan import StringAggPlan


class StringAggExecutor(AbstractExecutor):
    """
    Sort the frames which satisfy the condition

    Arguments:
        node (AbstractPlan): The OrderBy Plan

    """

    def __init__(self, db: EvaDBDatabase, node: StringAggPlan):
        super().__init__(db, node)
        self._string_agg_list = node.string_agg_list
        self._columns = node.columns
        self._separator = node.separator
        self._order_by = node.order_by
        self.batch_sizes = []

    def _extract_column_name(self, col):
        col_name = []
        if isinstance(col, TupleValueExpression):
            col_name += [col.col_alias]
        elif isinstance(col, FunctionExpression):
            col_name += col.col_alias
        elif isinstance(col, str):
            col_name += [col]
        else:
            raise ExecutorError(
                "Expression type {} is not supported.".format(type(col))
            )
        return col_name

    def extract_column_names(self):
        """extracts the string name of the column"""
        # self._columns: List[TupleValueExpression]
        col_name_list = []
        for col in self._columns:
            col_name_list += self._extract_column_name(col)
        return col_name_list

    def extract_separator(self):
        """extracts the sort type for the column"""
        # self._sort_types: List[ParserOrderBySortType]
        if isinstance(self._separator, str):
            return self._separator
        else:
            raise ExecutorError(
                "Expression type {} is not supported.".format(type(col))
            )
            return None

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]
        aggregated_batch_list = []

        # aggregates the batches into one large batch
        for batch in child_executor.exec(**kwargs):
            self.batch_sizes.append(len(batch))
            aggregated_batch_list.append(batch)
        aggregated_batch = Batch.concat(aggregated_batch_list, copy=False)

        # nothing to order by
        if not len(aggregated_batch):
            return

        # Column can be a functional expression, so if it
        # is not in columns, it needs to be re-evaluated.
        merge_batch_list = [aggregated_batch]
        for col in self._columns:
            col_name_list = self._extract_column_name(col)
            for col_name in col_name_list:
                if col_name not in aggregated_batch.columns:
                    batch = col.evaluate(aggregated_batch)
                    merge_batch_list.append(batch)
        if len(merge_batch_list) > 1:
            aggregated_batch = Batch.merge_column_wise(merge_batch_list)

        # sorts the batch
        try:
            # aggregated_batch.sort_orderby(
            #     by=self.extract_column_names(),
            #     sort_type=self.extract_sort_types(),
            # )
            aggregated_batch.join_columns_for_agg(self._columns)
            aggregated_batch.string_agg(self._separator, aggregated_batch_list, True)
            aggregated_batch.concat()
        except KeyError:
            # raise ExecutorError(str(e))
            pass

        # split the aggregated batch into smaller ones based
        #  on self.batch_sizes which holds the input batches sizes
        index = 0
        for i in self.batch_sizes:
            batch = aggregated_batch[index : index + i]
            batch.reset_index()
            index += i
            yield batch

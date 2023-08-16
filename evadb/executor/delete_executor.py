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

import pandas as pd
from sqlalchemy import and_, or_

from evadb.catalog.catalog_type import TableType
from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.expression.abstract_expression import ExpressionType
from evadb.expression.comparison_expression import ComparisonExpression
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.expression.logical_expression import LogicalExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.project_plan import ProjectPlan
from evadb.storage.storage_engine import StorageEngine


class DeleteExecutor(AbstractExecutor):
    """ """

    def __init__(self, db: EvaDBDatabase, node: ProjectPlan):
        super().__init__(db, node)
        self.predicate = node.where_clause

    def predicate_node_to_filter_clause(
        self, table: TableCatalogEntry, predicate_node: ComparisonExpression
    ):
        filter_clause = None
        left = predicate_node.get_child(0)
        right = predicate_node.get_child(1)

        if isinstance(left, TupleValueExpression):
            column = left.name
            x = table.columns[column]
        elif isinstance(left, ConstantValueExpression):
            value = left.value
            x = value
        else:
            left_filter_clause = self.predicate_node_to_filter_clause(table, left)

        if isinstance(right, TupleValueExpression):
            column = right.name
            y = table.columns[column]
        elif isinstance(right, ConstantValueExpression):
            value = right.value
            y = value
        else:
            right_filter_clause = self.predicate_node_to_filter_clause(table, right)

        if isinstance(predicate_node, LogicalExpression):
            if predicate_node.etype == ExpressionType.LOGICAL_AND:
                filter_clause = and_(left_filter_clause, right_filter_clause)
            elif predicate_node.etype == ExpressionType.LOGICAL_OR:
                filter_clause = or_(left_filter_clause, right_filter_clause)

        elif isinstance(predicate_node, ComparisonExpression):
            assert (
                predicate_node.etype != ExpressionType.COMPARE_CONTAINS
                and predicate_node.etype != ExpressionType.COMPARE_IS_CONTAINED
            ), f"Predicate type {predicate_node.etype} not supported in delete"

            if predicate_node.etype == ExpressionType.COMPARE_EQUAL:
                filter_clause = x == y
            elif predicate_node.etype == ExpressionType.COMPARE_GREATER:
                filter_clause = x > y
            elif predicate_node.etype == ExpressionType.COMPARE_LESSER:
                filter_clause = x < y
            elif predicate_node.etype == ExpressionType.COMPARE_GEQ:
                filter_clause = x >= y
            elif predicate_node.etype == ExpressionType.COMPARE_LEQ:
                filter_clause = x <= y
            elif predicate_node.etype == ExpressionType.COMPARE_NEQ:
                filter_clause = x != y

        return filter_clause

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        table_catalog = self.node.table_ref.table.table_obj
        storage_engine = StorageEngine.factory(self.db, table_catalog)

        assert (
            table_catalog.table_type == TableType.STRUCTURED_DATA
        ), "DELETE only implemented for structured data"

        table_to_delete_from = storage_engine._try_loading_table_via_reflection(
            table_catalog.name
        )

        sqlalchemy_filter_clause = self.predicate_node_to_filter_clause(
            table_to_delete_from, predicate_node=self.predicate
        )
        # verify where clause and convert to sqlalchemy supported filter
        # https://stackoverflow.com/questions/34026210/where-filter-from-table-object-using-a-dictionary-or-kwargs

        storage_engine.delete(table_catalog, sqlalchemy_filter_clause)
        yield Batch(pd.DataFrame(["Deleted rows"]))

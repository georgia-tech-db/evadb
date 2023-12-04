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
import pandas as pd
from sqlalchemy import and_, or_

from evadb.catalog.catalog_type import TableType
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.update_plan import UpdatePlan
from evadb.storage.storage_engine import StorageEngine

from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.expression.abstract_expression import ExpressionType
from evadb.expression.comparison_expression import ComparisonExpression
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.expression.logical_expression import LogicalExpression
from evadb.expression.tuple_value_expression import TupleValueExpression


class UpdateExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: UpdatePlan):
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
            # get index of column in table
            x = [i for i, x in enumerate(table.columns) if x.name == column][0]
            x = table.columns[x]
        elif isinstance(left, ConstantValueExpression):
            value = left.value
            x = value
        else:
            left_filter_clause = self.predicate_node_to_filter_clause(table, left)

        if isinstance(right, TupleValueExpression):
            column = right.name
            y = [i for i, y in enumerate(table.columns) if y.name == column][0]
            y = table.columns[y]
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
            ), f"Predicate type {predicate_node.etype} not supported in update"

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

    def exec(self, *args, **kwargs):
        storage_engine = None
        table_catalog_entry = None

        # Get catalog entry
        table_name = self.node.table_ref.table.table_name
        database_name = self.node.table_ref.table.database_name
        table_catalog_entry = self.catalog().get_table_catalog_entry(
            table_name, database_name
        )

        # Implemented only for STRUCTURED_DATA
        assert (
            table_catalog_entry.table_type == TableType.STRUCTURED_DATA
        ), "UPDATE only implemented for structured data"
        
        storage_engine = StorageEngine.factory(self.db, table_catalog_entry)
        table_to_update = storage_engine._try_loading_table_via_reflection(
            table_catalog_entry.name
        )

        values_to_update = [val_node.value for val_node in self.node.value_list]
        tuple_to_update = tuple(values_to_update)
        columns_to_update = [col_node.name for col_node in self.node.column_list]

        # Adding all values to Batch for update
        dataframe = pd.DataFrame([tuple_to_update], columns=columns_to_update)
        batch = Batch(dataframe)
        
        sqlalchemy_filter_clause = None
        
        if self.predicate != None:
            sqlalchemy_filter_clause = self.predicate_node_to_filter_clause(
                table_to_update, predicate_node=self.predicate
            )
        
        storage_engine.update(table_catalog_entry, batch, sqlalchemy_filter_clause)
        
        yield Batch(pd.DataFrame(["Updated rows"]))
        # yield Batch(
        #     pd.DataFrame([f"Number of rows loaded: {str(len(values_to_insert))}"])
        # )

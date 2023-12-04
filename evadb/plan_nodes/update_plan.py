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
from typing import List

from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.expression.abstract_expression import AbstractExpression
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType


class UpdatePlan(AbstractPlan):
    """This plan is used for storing information required for update
    operations.

    Args:
        table (TableCatalogEntry): table to update into
        column_list (List[AbstractExpression]): list of annotated column
        value_list (List[AbstractExpression]): list of abstract expression
                                                for the values to update
        where_clause (AbstractExpression): where clause for update
    """

    def __init__(
        self,
        table_ref: TableCatalogEntry,
        column_list: List[AbstractExpression],
        value_list: List[AbstractExpression],
        where_clause: AbstractExpression = None,
    ):
        super().__init__(PlanOprType.UPDATE)
        self._table_ref = table_ref
        self._column_list = column_list
        self._value_list = value_list
        self._where_clause = where_clause

    @property
    def table_ref(self):
        return self._table_ref
    
    @property
    def column_list(self):
        return self._column_list
    
    @property
    def value_list(self):
        return self._value_list

    @property
    def where_clause(self):
        return self._where_clause

    def __str__(self):
        return "UpdatePlan(table={}, \
            column_list={}, \
            value_list={}, \
            where_clause={})".format(
            self.table_ref, self.column_list, self.value_list, self.where_clause
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_ref,
                tuple(self.column_list),
                tuple(self.value_list),
                self.where_clause,
            )
        )

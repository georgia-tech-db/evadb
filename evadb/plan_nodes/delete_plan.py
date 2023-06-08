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
from evadb.expression.abstract_expression import AbstractExpression
from evadb.parser.table_ref import TableRef
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType


class DeletePlan(AbstractPlan):
    """This plan is used for storing information required for insert
    operations.

    Args:
        table (TableCatalogEntry): table to insert into
        column_list (List[AbstractExpression]): list of annotated column
        value_list (List[AbstractExpression]): list of abstract expression
                                                for the values to insert
    """

    def __init__(
        self,
        table_ref: TableRef,
        where_clause: AbstractExpression = None,
    ):
        super().__init__(PlanOprType.DELETE)
        self._table_ref = table_ref
        self._where_clause = where_clause

    @property
    def table_ref(self):
        return self._table_ref

    @property
    def where_clause(self):
        return self._where_clause

    def __str__(self):
        return "DeletePlan(table={}, \
            where_clause={})".format(
            self.table_ref, self._where_clause
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_ref,
                self._where_clause,
            )
        )

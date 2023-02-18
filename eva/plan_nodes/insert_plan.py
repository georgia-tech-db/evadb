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
from typing import List

from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.expression.abstract_expression import AbstractExpression
from eva.plan_nodes.abstract_plan import AbstractPlan
from eva.plan_nodes.types import PlanOprType


class InsertPlan(AbstractPlan):
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
        table: TableCatalogEntry,
        column_list: List[AbstractExpression],
        value_list: List[AbstractExpression],
    ):

        super().__init__(PlanOprType.INSERT)
        self.table = table
        self.columns_list = column_list
        self.value_list = value_list

    def __str__(self):
        return "InsertPlan(table={}, \
            column_list={}, \
            value_list={})".format(
            self.table, self.columns_list, self.value_list
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table,
                tuple(self.column_list),
                tuple(self.value_list),
            )
        )

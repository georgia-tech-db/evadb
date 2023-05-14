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
from eva.expression.abstract_expression import AbstractExpression
from eva.parser.table_ref import TableRef
from eva.plan_nodes.abstract_plan import AbstractPlan
from eva.plan_nodes.types import PlanOprType


class OverwritePlan(AbstractPlan):
    """
    This plan is used for storing information required for overwrite data
    operations.

    Arguments:
        table_ref(TableRef): table to overwrite data
        operation(AbstractExpression): overwrite the data with the result of operation
    """

    def __init__(self, table_ref: TableRef, operation: AbstractExpression):
        super().__init__(PlanOprType.OVERWRITE)
        self._table_ref = table_ref
        self._operation = operation

    @property
    def table_ref(self):
        return self._table_ref

    @property
    def operation(self):
        return self._operation

    def __str__(self):
        return "OverwritePlan(table_id={}, operation={})".format(
            self._table_ref,
            self._operation,
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self._table_ref,
                self._operation,
            )
        )

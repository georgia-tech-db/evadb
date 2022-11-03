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

from eva.expression.abstract_expression import AbstractExpression
from eva.planner.abstract_scan_plan import AbstractScan
from eva.planner.types import PlanOprType


class SeqScanPlan(AbstractScan):
    """
    This plan is used for storing information required for sequential scan
    operations.

    Arguments:
        columns: List[AbstractExpression]
            list of column names string in the plan
        predicate: AbstractExpression
            An expression used for filtering
    """

    def __init__(
        self,
        predicate: AbstractExpression,
        columns: List[AbstractExpression],
        alias: str = None,
    ):
        self._columns = columns
        self.alias = alias
        super().__init__(PlanOprType.SEQUENTIAL_SCAN, predicate)

    @property
    def columns(self):
        return self._columns

    def __str__(self):
        return "SeqScanPlan(predicate={}, \
            columns={}, \
            alias={})".format(
            self._predicate, self._columns, self.alias
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self.columns or []), self.alias))

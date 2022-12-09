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
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class GroupByPlan(AbstractPlan):
    """
    This plan is used for storing information required for group by
    operations.

    Arguments:
        groupby_clause: ConstantValueExpression
            A ConstantValueExpression which is the number of elements to
            group together.
    """

    def __init__(self, groupby_clause: ConstantValueExpression):
        self._groupby_clause = groupby_clause
        super().__init__(PlanOprType.GROUP_BY)

    @property
    def groupby_clause(self):
        return self._groupby_clause

    def __str__(self):
        return "GroupByPlan(groupby_clause={})".format(self._groupby_clause)

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.groupby_clause))

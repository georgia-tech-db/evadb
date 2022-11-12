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


class LimitPlan(AbstractPlan):
    """
    This plan is used for storing information required for limit
    operations.

    Arguments:
        limit_count: ConstantValueExpression
            A ConstantValueExpression which is the count of the
            number of rows returned
    """

    def __init__(self, limit_count: ConstantValueExpression):
        self._limit_count = limit_count
        super().__init__(PlanOprType.LIMIT)

    @property
    def limit_expression(self):
        return self._limit_count

    @property
    def limit_value(self):
        return self._limit_count.value

    def __str__(self):
        return "LimitPlan(limit_count={})".format(self._limit_count)

    def __hash__(self) -> int:
        return hash((super().__hash__(), self._limit_count))

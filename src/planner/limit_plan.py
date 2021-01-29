# coding=utf-8
# Copyright 2018-2020 EVA
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

from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanOprType
from src.expression.constant_value_expression import ConstantValueExpression


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
        super().__init__(PlanNodeType.LIMIT)

    @property
    def limit_expression(self):
        return self._limit_count

    @property
    def limit_value(self):
        return self._limit_count.value

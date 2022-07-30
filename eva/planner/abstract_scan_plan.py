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
"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from eva.expression.abstract_expression import AbstractExpression
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class AbstractScan(AbstractPlan):
    """Abstract class for all the scan based planners

    Arguments:
        predicate (AbstractExpression): An expression used for filtering
    """

    def __init__(self, opr_type: PlanOprType, predicate: AbstractExpression):
        super(AbstractScan, self).__init__(opr_type)
        self._predicate = predicate

    @property
    def predicate(self) -> AbstractExpression:
        return self._predicate

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.predicate))

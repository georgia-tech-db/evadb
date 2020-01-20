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
"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.expression.abstract_expression import AbstractExpression
from src.query_planner.abstract_plan import AbstractPlan

from src.query_planner.types import PlanNodeType


class AbstractScan(AbstractPlan):
    """Abstract class for all the scan based planners

    Arguments:
        predicate (AbstractExpression): An expression used for filtering
    """

    def __init__(self, node_type: PlanNodeType, predicate: AbstractExpression):
        super(AbstractScan, self).__init__(node_type)
        self._predicate = predicate

    @property
    def predicate(self) -> AbstractExpression:
        return self._predicate

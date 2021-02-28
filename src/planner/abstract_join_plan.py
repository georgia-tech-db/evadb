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


"""Abstract class for all the join planners
"""
from src.expression.abstract_expression import AbstractExpression
from src.planner.abstract_plan import AbstractPlan
from src.parser.types import JoinType

from src.planner.types import PlanNodeType


class AbstractJoin(AbstractPlan):
    """Abstract class for all the join based planners

    Arguments:
        join_type: JoinType
            type of join, INNER, OUTER , LATERAL etc
        join_predicate: AbstractExpression
            An expression used for joining
    """

    def __init__(self,
                 node_type: PlanNodeType,
                 join_type: JoinType,
                 join_predicate: AbstractExpression):
        super().__init__(node_type)
        self._join_type = join_type
        self._join_predicate = join_predicate

    @property
    def join_type(self) -> AbstractExpression:
        return self._join_type

    @property
    def join_predicate(self) -> AbstractExpression:
        return self._join_predicate

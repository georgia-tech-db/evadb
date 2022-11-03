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
from eva.parser.types import JoinType
from eva.planner.abstract_join_plan import AbstractJoin
from eva.planner.types import PlanOprType


class LateralJoinPlan(AbstractJoin):
    """
    This plan is used for storing information required for lateral join
    """

    def __init__(self, join_predicate: AbstractExpression):
        self.join_project = []
        super().__init__(
            PlanOprType.LATERAL_JOIN, JoinType.LATERAL_JOIN, join_predicate
        )

    def __str__(self):
        return "LateralJoinPlan(join_project={}, \
            join_predicate={})".format(
            self.join_project, self.join_predicate
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self.join_project)))

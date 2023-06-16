# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from evadb.expression.abstract_expression import AbstractExpression
from evadb.parser.types import JoinType
from evadb.plan_nodes.abstract_join_plan import AbstractJoin
from evadb.plan_nodes.types import PlanOprType


class NestedLoopJoinPlan(AbstractJoin):
    """
    This plan is used for storing information required for a nested loop join.
    """

    def __init__(self, join_type: JoinType, join_predicate: AbstractExpression = None):
        self._join_predicate = join_predicate
        super().__init__(PlanOprType.NESTED_LOOP_JOIN, join_type, join_predicate)

    @property
    def join_predicate(self):
        return self._join_predicate

    def __str__(self):
        return "NestedLoopJoinPlan(join_type={}, \
            predicate={})".format(
            self.join_type, self.join_predicate
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.join_type, self.join_predicate))

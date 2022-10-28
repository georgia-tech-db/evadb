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
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class ProjectPlan(AbstractPlan):
    """
    Arguments:
        target_list List[(AbstractExpression)]: projection list
    """

    def __init__(self, target_list: List[AbstractExpression]):
        self.target_list = target_list
        super().__init__(PlanOprType.PROJECT)

    def __str__(self):
        return "ProjectPlan(target_list={})".format(self.target_list)

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self.target_list)))

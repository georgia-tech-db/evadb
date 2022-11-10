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
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class ExplainPlan(AbstractPlan):
    def __init__(self, explainable_plan: AbstractPlan):
        super().__init__(PlanOprType.EXPLAIN)
        self._explainable_plan = explainable_plan

    @property
    def explainable_plan(self):
        return self._explainable_plan

    def __str__(self) -> str:
        return "ExplainPlan()"

    def __hash__(self) -> int:
        return hash((super().__hash__(), self._explainable_plan))

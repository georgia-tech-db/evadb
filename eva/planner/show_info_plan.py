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
from eva.parser.types import ShowType
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class ShowInfoPlan(AbstractPlan):
    def __init__(self, show_type: ShowType):
        self._show_type = show_type
        super().__init__(PlanOprType.SHOW_INFO)

    @property
    def show_type(self):
        return self._show_type

    def __str__(self):
        return "ShowUDFPlan" if self._show_type == ShowType.UDF else "ShowTablePlan"

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.show_type))

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
from src.optimizer.generators.base import Generator
from src.optimizer.operators import LogicalCreate, Operator
from src.planner.create_plan import CreatePlan


class CreateGenerator(Generator):
    def __init__(self):
        self._video_ref = None
        self._col_list = None
        self._if_not_exists = None

    def _visit_logical_create(self, operator: LogicalCreate):
        self._video_ref = operator.video
        self._col_list = operator.column_list
        self._if_not_exists = operator.if_not_exists

    def _visit(self, operator: Operator):
        for child in operator.children:
            self._visit(child)

        if isinstance(operator, LogicalCreate):
            self._visit_logical_create(operator)

    def build(self, operator: Operator):
        self.__init__()
        self._visit(operator)
        create_plan = CreatePlan(
            self._video_ref,
            self._col_list,
            self._if_not_exists)
        return create_plan

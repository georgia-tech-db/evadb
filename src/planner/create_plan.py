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
from src.planner.types import PlanNodeType


class CreatePlan(AbstractPlan):
    def __init__(self, table_name, column_list, file_url):
        super().__init__(PlanNodeType.CREATE)
        self._table_name = table_name
        self._file_url = file_url
        self._columns = column_list

    @property
    def table_name(self):
        return self._table_name

    @property
    def file_url(self):
        return self._file_url

    @property
    def columns(self):
        return self._columns

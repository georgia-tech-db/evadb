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
from src.optimizer.operators import LogicalLoadData, Operator
from src.planner.load_data_plan import LoadDataPlan


class LoadDataGenerator(Generator):
    def __init__(self):
        self._table_metainfo = None
        self._path = None

    def _visit(self, operator: Operator):
        if isinstance(operator, LogicalLoadData):
            self._table_metainfo = operator.table_metainfo
            self._path = operator.path

    def build(self, operator: Operator):
        self.__init__()
        self._visit(operator)
        load_plan = LoadDataPlan(self._table_metainfo, self._path)
        return load_plan

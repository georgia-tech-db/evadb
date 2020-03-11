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
from src.optimizer.operators import LogicalGet, Operator, LogicalFilter, \
    LogicalProject
from src.planner.seq_scan_plan import SeqScanPlan
from src.planner.storage_plan import StoragePlan


class ScanGenerator(Generator):
    def __init__(self):
        self._target_list = None
        self._predicate = None
        self._plan = None

    def _visit_logical_get(self, operator: LogicalGet):
        self._plan = StoragePlan(operator.dataset_metadata)

    def _visit_logical_filter(self, operator: LogicalFilter):
        self._predicate = operator.predicate

    def _visit_logical_project(self, operator: LogicalProject):
        self._target_list = operator.target_list

    def _visit(self, operator: Operator):
        for child in operator.children:
            self._visit(child)

        if isinstance(operator, LogicalGet):
            self._visit_logical_get(operator)

        if isinstance(operator, LogicalFilter):
            self._visit_logical_filter(operator)

        if isinstance(operator, LogicalProject):
            self._visit_logical_project(operator)

    def build(self, operator: Operator):
        self.__init__()
        self._visit(operator)
        seq_scan = SeqScanPlan(self._predicate, self._target_list)
        seq_scan.append_child(self._plan)
        return seq_scan

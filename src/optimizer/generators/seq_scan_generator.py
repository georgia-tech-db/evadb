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
    LogicalProject, LogicalUnion, LogicalOrderBy, LogicalLimit, LogicalJoin, \
    LogicalFunctionScan
from src.planner.seq_scan_plan import SeqScanPlan
from src.planner.union_plan import UnionPlan
from src.planner.storage_plan import StoragePlan
from src.planner.orderby_plan import OrderByPlan
from src.planner.limit_plan import LimitPlan
from src.planner.nested_loop_join_plan import NestedLoopJoin
from src.planner.function_scan import FunctionScan


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
        seq_scan = SeqScanPlan(self._predicate, self._target_list)
        if self._plan:
            seq_scan.append_child(self._plan)
        self._plan = seq_scan

    def _visit_logical_union(self, operator: LogicalUnion):
        union = UnionPlan(operator.all)
        self._visit(operator.children[0])
        union.append_child(self._plan)
        self._visit(operator.children[1])
        union.append_child(self._plan)
        self._plan = union

    def _visit_logical_orderby(self, operator: LogicalOrderBy):
        orderbyplan = OrderByPlan(operator.orderby_list)
        orderbyplan.append_child(self._plan)
        self._plan = orderbyplan

    def _visit_logical_limit(self, operator: LogicalLimit):
        limitplan = LimitPlan(operator.limit_count)
        limitplan.append_child(self._plan)
        self._plan = limitplan

    def _visit_logical_join(self, operator: LogicalJoin):
        joinplan = NestedLoopJoin(operator.join_type, operator.join_predicate)
        self._plan = joinplan

    def _visit(self, operator: Operator):
        if isinstance(operator, LogicalUnion):
            self._visit_logical_union(operator)
            return

        for child in operator.children:
            self._visit(child)

        if isinstance(operator, LogicalFunctionScan):
            self._plan = FunctionScan(operator.func_expr)

        if isinstance(operator, LogicalJoin):
            self._visit_logical_join(operator)

        if isinstance(operator, LogicalOrderBy):
            self._visit_logical_orderby(operator)

        if isinstance(operator, LogicalLimit):
            self._visit_logical_limit(operator)

        if isinstance(operator, LogicalGet):
            self._visit_logical_get(operator)

        if isinstance(operator, LogicalFilter):
            self._visit_logical_filter(operator)

        if isinstance(operator, LogicalProject):
            self._visit_logical_project(operator)

    def build(self, operator: Operator):
        self.__init__()
        self._visit(operator)
        return self._plan

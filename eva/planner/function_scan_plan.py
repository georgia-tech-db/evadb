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
from eva.expression.function_expression import FunctionExpression
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class FunctionScanPlan(AbstractPlan):
    """
    This plan used to store metadata to perform function table scan.

    Arguments:
        func_expr(FunctionExpression): parameterized function expression that
            reference columns from a table expression that precedes it.
        do_unnest(bool): if True perform unnest operation on the output of FunctionScan
    """

    def __init__(self, func_expr: FunctionExpression, do_unnest: bool = False):
        self._func_expr = func_expr
        self._do_unnest = do_unnest
        super().__init__(PlanOprType.FUNCTION_SCAN)

    @property
    def func_expr(self):
        return self._func_expr

    @property
    def do_unnest(self):
        return self._do_unnest

    def __str__(self):
        plan = "UnnestFunctionScanPlan" if self._do_unnest else "FunctionScanPlan"
        return "{}(func_expr={})".format(plan, self._func_expr)

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.func_expr, self.do_unnest))

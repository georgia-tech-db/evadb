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
from evadb.expression.function_expression import FunctionExpression
from evadb.parser.alias import Alias
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType


class ApplyAndMergePlan(AbstractPlan):
    """
    This dataclass stores metadata to perform apply and merge operation.

    Arguments:
        func_expr(FunctionExpression): parameterized function expression that
            reference columns from a table expression that precedes it.
        do_unnest(bool): if True perform unnest operation on the output of FunctionScan
    """

    def __init__(
        self, func_expr: FunctionExpression, alias: Alias, do_unnest: bool = False
    ):
        self._func_expr = func_expr
        self._alias = alias
        self._do_unnest = do_unnest
        super().__init__(PlanOprType.APPLY_AND_MERGE)

    @property
    def func_expr(self):
        return self._func_expr

    @property
    def alias(self):
        return self._alias

    @property
    def do_unnest(self):
        return self._do_unnest

    def __str__(self):
        plan = "UnnestApplyAndMergePlan" if self._do_unnest else "ApplyAndMergePlan"
        return "{}(func_expr={})".format(plan, self._func_expr)

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.func_expr, self.alias, self.do_unnest))

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


class LLMPlan(AbstractPlan):
    def __init__(self, llm_expr: FunctionExpression):
        self.llm_expr = llm_expr
        self.alias = llm_expr.alias
        super().__init__(PlanOprType.LLM)

    def __str__(self):
        return f"LLMPlan(llm_expr={self.llm_expr})"

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.llm_expr, self.alias))

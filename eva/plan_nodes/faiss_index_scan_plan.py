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
from eva.plan_nodes.abstract_plan import AbstractPlan
from eva.plan_nodes.types import PlanOprType


class FaissIndexScanPlan(AbstractPlan):
    def __init__(self, index_name: str, query_num: int, query_expr: FunctionExpression):
        super().__init__(PlanOprType.FAISS_INDEX_SCAN)
        self._index_name = index_name
        self._query_num = query_num
        self._query_expr = query_expr

    @property
    def index_name(self):
        return self._index_name

    @property
    def query_num(self):
        return self._query_num

    @property
    def query_expr(self):
        return self._query_expr

    def __str__(self):
        return "FaissIndexScan(index_name={}, query_num={}, query_expr={})".format(
            self._index_name, self._query_num, self._query_expr
        )

    def __hash__(self) -> int:
        return hash(
            (super().__hash__(), self.index_name, self.query_num, self.query_expr)
        )

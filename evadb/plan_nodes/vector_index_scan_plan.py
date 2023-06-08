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
from evadb.catalog.catalog_type import VectorStoreType
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.expression.function_expression import FunctionExpression
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType


class VectorIndexScanPlan(AbstractPlan):
    """
    The plan first evaluates the `search_query_expr` expression and searches the output
    in the vector index. The plan finally projects `limit_count` number of results.

    Arguments:
        index_name (str): The vector index name.
        limit_count (ConstantValueExpression): Number of top results to project.
        search_query_expr (FunctionExpression): function expression to evaluate, whose
        results will be searched in the vector index.
    """

    def __init__(
        self,
        index_name: str,
        vector_store_type: VectorStoreType,
        limit_count: ConstantValueExpression,
        search_query_expr: FunctionExpression,
    ):
        super().__init__(PlanOprType.VECTOR_INDEX_SCAN)
        self._index_name = index_name
        self._vector_store_type = vector_store_type
        self._limit_count = limit_count
        self._search_query_expr = search_query_expr

    @property
    def index_name(self):
        return self._index_name

    @property
    def vector_store_type(self):
        return self._vector_store_type

    @property
    def limit_count(self):
        return self._limit_count

    @property
    def search_query_expr(self):
        return self._search_query_expr

    def __str__(self):
        return "VectorIndexScan(index_name={}, vector_store_type={}, limit_count={}, search_query_expr={})".format(
            self._index_name,
            self.vector_store_type,
            self._limit_count,
            self._search_query_expr,
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.index_name,
                self.vector_store_type,
                self.limit_count,
                self.search_query_expr,
            )
        )

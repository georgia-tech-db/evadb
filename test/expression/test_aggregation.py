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
import unittest

from src.expression.abstract_expression import ExpressionType
from src.expression.aggregation_expression import AggregationExpression
from src.expression.tuple_value_expression import TupleValueExpression


class AggregationExpressionsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_aggregation_sum(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_SUM,
            None,
            columnName
        )
        tuple1 = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        self.assertEqual(6, aggr_expr.evaluate(tuple1, None))

    def test_aggregation_count(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_COUNT,
            None,
            columnName
        )
        tuple1 = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        self.assertEqual(3, aggr_expr.evaluate(tuple1, None))

    def test_aggregation_avg(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_AVG,
            None,
            columnName
        )
        tuple1 = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        self.assertEqual(2, aggr_expr.evaluate(tuple1, None))

    def test_aggregation_min(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_MIN,
            None,
            columnName
        )
        tuple1 = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        self.assertEqual(1, aggr_expr.evaluate(tuple1, None))

    def test_aggregation_max(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_MAX,
            None,
            columnName
        )
        tuple1 = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        self.assertEqual(3, aggr_expr.evaluate(tuple1, None))
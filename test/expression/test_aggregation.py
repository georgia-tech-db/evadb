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
import unittest

import numpy as np
import pandas as pd

from eva.expression.abstract_expression import ExpressionType
from eva.expression.aggregation_expression import AggregationExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.models.storage.batch import Batch


class AggregationExpressionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_aggregation_first(self):
        columnName = TupleValueExpression(col_name=0)
        columnName.col_alias = 0
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_FIRST, None, columnName
        )
        tuples = Batch(pd.DataFrame({0: [1, 2, 3], 1: [2, 3, 4], 2: [3, 4, 5]}))
        batch = aggr_expr.evaluate(tuples, None)
        self.assertEqual(1, batch.frames.iloc[0][0])

    def test_aggregation_last(self):
        columnName = TupleValueExpression(col_name=0)
        columnName.col_alias = 0
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_LAST, None, columnName
        )
        tuples = Batch(pd.DataFrame({0: [1, 2, 3], 1: [2, 3, 4], 2: [3, 4, 5]}))
        batch = aggr_expr.evaluate(tuples, None)
        self.assertEqual(3, batch.frames.iloc[0][0])

    def test_aggregation_segment(self):
        columnName = TupleValueExpression(col_name=0)
        columnName.col_alias = 0
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_SEGMENT, None, columnName
        )
        tuples = Batch(pd.DataFrame({0: [1, 2, 3], 1: [2, 3, 4], 2: [3, 4, 5]}))
        batch = aggr_expr.evaluate(tuples, None)
        self.assertTrue((np.array([1, 2, 3]) == batch.frames.iloc[0][0]).all())

    def test_aggregation_sum(self):
        columnName = TupleValueExpression(col_name=0)
        columnName.col_alias = 0
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_SUM, None, columnName
        )
        tuples = Batch(pd.DataFrame({0: [1, 2, 3], 1: [2, 3, 4], 2: [3, 4, 5]}))
        batch = aggr_expr.evaluate(tuples, None)
        self.assertEqual(6, batch.frames.iloc[0][0])

    def test_aggregation_count(self):
        columnName = TupleValueExpression(col_name=0)
        columnName.col_alias = 0
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_COUNT, None, columnName
        )
        tuples = Batch(pd.DataFrame({0: [1, 2, 3], 1: [2, 3, 4], 2: [3, 4, 5]}))
        batch = aggr_expr.evaluate(tuples, None)
        self.assertEqual(3, batch.frames.iloc[0][0])

    def test_aggregation_avg(self):
        columnName = TupleValueExpression(col_name=0)
        columnName.col_alias = 0
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_AVG, None, columnName
        )
        tuples = Batch(pd.DataFrame({0: [1, 2, 3], 1: [2, 3, 4], 2: [3, 4, 5]}))
        batch = aggr_expr.evaluate(tuples, None)
        self.assertEqual(2, batch.frames.iloc[0][0])

    def test_aggregation_min(self):
        columnName = TupleValueExpression(col_name=0)
        columnName.col_alias = 0
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_MIN, None, columnName
        )
        tuples = Batch(pd.DataFrame({0: [1, 2, 3], 1: [2, 3, 4], 2: [3, 4, 5]}))
        batch = aggr_expr.evaluate(tuples, None)
        self.assertEqual(1, batch.frames.iloc[0][0])

    def test_aggregation_max(self):
        columnName = TupleValueExpression(col_name=0)
        columnName.col_alias = 0
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_MAX, None, columnName
        )
        tuples = Batch(pd.DataFrame({0: [1, 2, 3], 1: [2, 3, 4], 2: [3, 4, 5]}))
        batch = aggr_expr.evaluate(tuples, None)
        self.assertEqual(3, batch.frames.iloc[0][0])

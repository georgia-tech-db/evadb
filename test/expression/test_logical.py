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
import unittest

import pandas as pd
from mock import Mock

from evadb.expression.abstract_expression import ExpressionType
from evadb.expression.comparison_expression import ComparisonExpression
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.expression.logical_expression import LogicalExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.models.storage.batch import Batch


class LogicalExpressionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create a dummy batch
        self.batch = Batch(pd.DataFrame([0]))

    def test_logical_and(self):
        const_exp1 = ConstantValueExpression(1)
        const_exp2 = ConstantValueExpression(1)

        comparison_expression_left = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL, const_exp1, const_exp2
        )
        const_exp1 = ConstantValueExpression(2)
        const_exp2 = ConstantValueExpression(1)
        comparison_expression_right = ComparisonExpression(
            ExpressionType.COMPARE_GREATER, const_exp1, const_exp2
        )
        logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_AND,
            comparison_expression_left,
            comparison_expression_right,
        )
        self.assertEqual([True], logical_expr.evaluate(self.batch).frames[0].tolist())

    def test_logical_or(self):
        const_exp1 = ConstantValueExpression(1)
        const_exp2 = ConstantValueExpression(1)

        comparison_expression_left = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL, const_exp1, const_exp2
        )
        const_exp1 = ConstantValueExpression(1)
        const_exp2 = ConstantValueExpression(2)
        comparison_expression_right = ComparisonExpression(
            ExpressionType.COMPARE_GREATER, const_exp1, const_exp2
        )
        logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            comparison_expression_left,
            comparison_expression_right,
        )
        self.assertEqual([True], logical_expr.evaluate(self.batch).frames[0].tolist())

    def test_logical_not(self):
        const_exp1 = ConstantValueExpression(0)
        const_exp2 = ConstantValueExpression(1)

        comparison_expression_right = ComparisonExpression(
            ExpressionType.COMPARE_GREATER, const_exp1, const_exp2
        )
        logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_NOT, None, comparison_expression_right
        )
        self.assertEqual([True], logical_expr.evaluate(self.batch).frames[0].tolist())

    def test_short_circuiting_and_complete(self):
        # tests whether right-hand side is bypassed completely with and
        tup_val_exp_l = TupleValueExpression(col_name=0)
        tup_val_exp_l.col_alias = 0
        tup_val_exp_r = TupleValueExpression(col_name=1)
        tup_val_exp_r.col_alias = 1

        comp_exp_l = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL, tup_val_exp_l, tup_val_exp_r
        )
        comp_exp_r = Mock(spec=ComparisonExpression)

        logical_exp = LogicalExpression(
            ExpressionType.LOGICAL_AND, comp_exp_l, comp_exp_r
        )

        tuples = Batch(pd.DataFrame({0: [1, 2, 3], 1: [4, 5, 6]}))
        self.assertEqual(
            [False, False, False], logical_exp.evaluate(tuples).frames[0].tolist()
        )
        comp_exp_r.evaluate.assert_not_called()

    def test_short_circuiting_or_complete(self):
        # tests whether right-hand side is bypassed completely with or
        tup_val_exp_l = TupleValueExpression(col_name=0)
        tup_val_exp_l.col_alias = 0
        tup_val_exp_r = TupleValueExpression(col_name=1)
        tup_val_exp_r.col_alias = 1

        comp_exp_l = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL, tup_val_exp_l, tup_val_exp_r
        )
        comp_exp_r = Mock(spec=ComparisonExpression)

        logical_exp = LogicalExpression(
            ExpressionType.LOGICAL_OR, comp_exp_l, comp_exp_r
        )

        tuples = Batch(pd.DataFrame({0: [1, 2, 3], 1: [1, 2, 3]}))
        self.assertEqual(
            [True, True, True], logical_exp.evaluate(tuples).frames[0].tolist()
        )
        comp_exp_r.evaluate.assert_not_called()

    def test_short_circuiting_and_partial(self):
        # tests whether right-hand side is partially executed with and
        tup_val_exp_l = TupleValueExpression(col_name=0)
        tup_val_exp_l.col_alias = 0
        tup_val_exp_r = TupleValueExpression(col_name=1)
        tup_val_exp_r.col_alias = 1

        comp_exp_l = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL, tup_val_exp_l, tup_val_exp_r
        )
        comp_exp_r = Mock(spec=ComparisonExpression)
        comp_exp_r.evaluate = Mock(return_value=Mock(_frames=[[True], [False]]))

        logical_exp = LogicalExpression(
            ExpressionType.LOGICAL_AND, comp_exp_l, comp_exp_r
        )

        tuples = Batch(pd.DataFrame({0: [1, 2, 3, 4], 1: [1, 2, 5, 6]}))
        self.assertEqual(
            [True, False, False, False], logical_exp.evaluate(tuples).frames[0].tolist()
        )
        comp_exp_r.evaluate.assert_called_once_with(tuples[[0, 1]])

    def test_short_circuiting_or_partial(self):
        # tests whether right-hand side is partially executed with or
        tup_val_exp_l = TupleValueExpression(col_name=0)
        tup_val_exp_l.col_alias = 0
        tup_val_exp_r = TupleValueExpression(col_name=1)
        tup_val_exp_r.col_alias = 1

        comp_exp_l = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL, tup_val_exp_l, tup_val_exp_r
        )
        comp_exp_r = Mock(spec=ComparisonExpression)
        comp_exp_r.evaluate = Mock(return_value=Mock(_frames=[[True], [False]]))

        logical_exp = LogicalExpression(
            ExpressionType.LOGICAL_OR, comp_exp_l, comp_exp_r
        )

        tuples = Batch(pd.DataFrame({0: [1, 2, 3, 4], 1: [5, 6, 3, 4]}))
        self.assertEqual(
            [True, False, True, True], logical_exp.evaluate(tuples).frames[0].tolist()
        )
        comp_exp_r.evaluate.assert_called_once_with(tuples[[0, 1]])

    def test_multiple_logical(self):
        batch = Batch(pd.DataFrame({"col": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}))

        # col > 1
        comp_left = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
            TupleValueExpression(col_alias="col"),
            ConstantValueExpression(1),
        )

        batch_copy = Batch(pd.DataFrame({"col": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}))
        expected = batch[list(range(2, 10))]
        batch_copy.drop_zero(comp_left.evaluate(batch))
        self.assertEqual(batch_copy, expected)

        # col < 8
        comp_right = ComparisonExpression(
            ExpressionType.COMPARE_LESSER,
            TupleValueExpression(col_alias="col"),
            ConstantValueExpression(8),
        )

        batch_copy = Batch(pd.DataFrame({"col": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}))
        expected = batch[list(range(0, 8))]
        batch_copy.drop_zero(comp_right.evaluate(batch))
        self.assertEqual(batch_copy, expected)

        # col >= 5
        comp_expr = ComparisonExpression(
            ExpressionType.COMPARE_GEQ,
            TupleValueExpression(col_alias="col"),
            ConstantValueExpression(5),
        )
        batch_copy = Batch(pd.DataFrame({"col": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}))
        expected = batch[list(range(5, 10))]
        batch_copy.drop_zero(comp_expr.evaluate(batch))
        self.assertEqual(batch_copy, expected)

        # (col >= 5)  AND (col > 1 AND col < 8)
        l_expr = LogicalExpression(ExpressionType.LOGICAL_AND, comp_left, comp_right)
        root_l_expr = LogicalExpression(ExpressionType.LOGICAL_AND, comp_expr, l_expr)
        batch_copy = Batch(pd.DataFrame({"col": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}))
        expected = batch[[5, 6, 7]]
        batch_copy.drop_zero(root_l_expr.evaluate(batch))
        self.assertEqual(batch_copy, expected)

        # (col > 1 AND col < 8) AND (col >= 5)
        root_l_expr = LogicalExpression(ExpressionType.LOGICAL_AND, l_expr, comp_expr)
        batch_copy = Batch(pd.DataFrame({"col": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}))
        expected = batch[[5, 6, 7]]
        batch_copy.drop_zero(root_l_expr.evaluate(batch))
        self.assertEqual(batch_copy, expected)

        # (col >=4 AND col <= 7) AND (col > 1 AND col < 8)
        between_4_7 = LogicalExpression(
            ExpressionType.LOGICAL_AND,
            ComparisonExpression(
                ExpressionType.COMPARE_GEQ,
                TupleValueExpression(col_alias="col"),
                ConstantValueExpression(4),
            ),
            ComparisonExpression(
                ExpressionType.COMPARE_LEQ,
                TupleValueExpression(col_alias="col"),
                ConstantValueExpression(7),
            ),
        )
        test_expr = LogicalExpression(ExpressionType.LOGICAL_AND, between_4_7, l_expr)
        batch_copy = Batch(pd.DataFrame({"col": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}))
        expected = batch[[4, 5, 6, 7]]
        batch_copy.drop_zero(test_expr.evaluate(batch))
        self.assertEqual(batch_copy, expected)

        # (col >=4 AND col <= 7) OR (col > 1 AND col < 8)
        test_expr = LogicalExpression(ExpressionType.LOGICAL_OR, between_4_7, l_expr)
        batch_copy = Batch(pd.DataFrame({"col": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}))
        expected = batch[[2, 3, 4, 5, 6, 7]]
        batch_copy.drop_zero(test_expr.evaluate(batch))
        self.assertEqual(batch_copy, expected)

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

import pandas as pd
from mock import Mock

from eva.expression.abstract_expression import ExpressionType
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.logical_expression import LogicalExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.models.storage.batch import Batch


class LogicalExpressionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        self.assertEqual([True], logical_expr.evaluate(None).frames[0].tolist())

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
        self.assertEqual([True], logical_expr.evaluate(None).frames[0].tolist())

    def test_logical_not(self):
        const_exp1 = ConstantValueExpression(0)
        const_exp2 = ConstantValueExpression(1)

        comparison_expression_right = ComparisonExpression(
            ExpressionType.COMPARE_GREATER, const_exp1, const_exp2
        )
        logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_NOT, None, comparison_expression_right
        )
        self.assertEqual([True], logical_expr.evaluate(None).frames[0].tolist())

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
        comp_exp_r.evaluate.assert_called_once_with(tuples, mask=[0, 1])

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
        comp_exp_r.evaluate.assert_called_once_with(tuples, mask=[0, 1])

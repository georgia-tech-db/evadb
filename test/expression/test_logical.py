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
from src.expression.comparison_expression import ComparisonExpression
from src.expression.logical_expression import LogicalExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression


class LogicalExpressionsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_logical_and(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        comparison_expression_left = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL,
            tpl_exp,
            const_exp
        )
        tpl_exp = TupleValueExpression(1)
        const_exp = ConstantValueExpression(1)
        comparison_expression_right = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
            tpl_exp,
            const_exp
        )
        logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_AND,
            comparison_expression_left,
            comparison_expression_right
        )
        tuple1 = [[1], [2], 3]
        self.assertEqual([True], logical_expr.evaluate(tuple1, None))

    def test_comparison_compare_greater(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        comparison_expression_left = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL,
            tpl_exp,
            const_exp
        )
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)
        comparison_expression_right = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
            tpl_exp,
            const_exp
        )
        logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            comparison_expression_left,
            comparison_expression_right
        )
        tuple1 = [[1], 2, 3]
        self.assertEqual([True], logical_expr.evaluate(tuple1, None))

    def test_logical_not(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        comparison_expression_right = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
            tpl_exp,
            const_exp
        )
        logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_NOT,
            None,
            comparison_expression_right
        )
        tuple1 = [[1], 2, 3]
        self.assertEqual([True], logical_expr.evaluate(tuple1, None))

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

from eva.catalog.column_type import ColumnType
from eva.expression.abstract_expression import ExpressionType
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.constant_value_expression import ConstantValueExpression


class ComparisonExpressionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_comparison_compare_equal(self):
        const_exp1 = ConstantValueExpression(1)
        const_exp2 = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL, const_exp1, const_exp2
        )
        self.assertEqual([True], cmpr_exp.evaluate(None).frames[0].tolist())

    def test_comparison_compare_greater(self):
        const_exp1 = ConstantValueExpression(1)
        const_exp2 = ConstantValueExpression(0)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_GREATER, const_exp1, const_exp2
        )
        self.assertEqual([True], cmpr_exp.evaluate(None).frames[0].tolist())

    def test_comparison_compare_lesser(self):
        const_exp1 = ConstantValueExpression(0)
        const_exp2 = ConstantValueExpression(2)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_LESSER, const_exp1, const_exp2
        )
        self.assertEqual([True], cmpr_exp.evaluate(None).frames[0].tolist())

    def test_comparison_compare_geq(self):
        const_exp1 = ConstantValueExpression(1)
        const_exp2 = ConstantValueExpression(1)
        const_exp3 = ConstantValueExpression(0)

        cmpr_exp1 = ComparisonExpression(
            ExpressionType.COMPARE_GEQ, const_exp1, const_exp2
        )

        cmpr_exp2 = ComparisonExpression(
            ExpressionType.COMPARE_GEQ, const_exp1, const_exp3
        )
        # checking equal
        self.assertEqual([True], cmpr_exp1.evaluate(None).frames[0].tolist())
        # checking greater equal
        self.assertEqual([True], cmpr_exp2.evaluate(None).frames[0].tolist())

    def test_comparison_compare_leq(self):
        const_exp1 = ConstantValueExpression(0)
        const_exp2 = ConstantValueExpression(2)
        const_exp3 = ConstantValueExpression(2)

        cmpr_exp1 = ComparisonExpression(
            ExpressionType.COMPARE_LEQ, const_exp1, const_exp2
        )

        cmpr_exp2 = ComparisonExpression(
            ExpressionType.COMPARE_LEQ, const_exp2, const_exp3
        )

        # checking lesser
        self.assertEqual([True], cmpr_exp1.evaluate(None).frames[0].tolist())
        # checking equal
        self.assertEqual([True], cmpr_exp2.evaluate(None).frames[0].tolist())

    def test_comparison_compare_neq(self):
        const_exp1 = ConstantValueExpression(0)
        const_exp2 = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_NEQ, const_exp1, const_exp2
        )

        self.assertEqual([True], cmpr_exp.evaluate(None).frames[0].tolist())

    def test_comparison_compare_contains(self):
        const_exp1 = ConstantValueExpression([1, 2], ColumnType.NDARRAY)
        const_exp2 = ConstantValueExpression([1, 5], ColumnType.NDARRAY)
        const_exp3 = ConstantValueExpression([1, 2, 3, 4], ColumnType.NDARRAY)

        cmpr_exp1 = ComparisonExpression(
            ExpressionType.COMPARE_CONTAINS, const_exp3, const_exp1
        )

        self.assertEqual([True], cmpr_exp1.evaluate(None).frames[0].tolist())

        cmpr_exp2 = ComparisonExpression(
            ExpressionType.COMPARE_CONTAINS, const_exp3, const_exp2
        )

        self.assertEqual([False], cmpr_exp2.evaluate(None).frames[0].tolist())

    def test_comparison_compare_is_contained(self):
        const_exp1 = ConstantValueExpression([1, 2], ColumnType.NDARRAY)
        const_exp2 = ConstantValueExpression([1, 5], ColumnType.NDARRAY)
        const_exp3 = ConstantValueExpression([1, 2, 3, 4], ColumnType.NDARRAY)

        cmpr_exp1 = ComparisonExpression(
            ExpressionType.COMPARE_IS_CONTAINED, const_exp1, const_exp3
        )

        self.assertEqual([True], cmpr_exp1.evaluate(None).frames[0].tolist())

        cmpr_exp2 = ComparisonExpression(
            ExpressionType.COMPARE_IS_CONTAINED, const_exp2, const_exp3
        )

        self.assertEqual([False], cmpr_exp2.evaluate(None).frames[0].tolist())

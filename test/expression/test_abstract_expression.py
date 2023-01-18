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

from eva.expression.abstract_expression import ExpressionType
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.logical_expression import LogicalExpression
from eva.expression.tuple_value_expression import TupleValueExpression


class AbstractExpressionsTest(unittest.TestCase):
    def test_walk(self):
        const_exp1 = ConstantValueExpression(1)
        const_exp2 = ConstantValueExpression(1)
        const_exp3 = ConstantValueExpression(0)
        const_exp4 = ConstantValueExpression(5)

        cmpr_exp1 = ComparisonExpression(
            ExpressionType.COMPARE_GEQ, const_exp1, const_exp2
        )

        cmpr_exp2 = ComparisonExpression(
            ExpressionType.COMPARE_GEQ, const_exp3, const_exp4
        )

        expr = LogicalExpression(ExpressionType.LOGICAL_AND, cmpr_exp1, cmpr_exp2)

        self.assertEqual(len(list(expr.walk())), 7)
        self.assertEqual(len(list(expr.walk(bfs=False))), 7)

        bfs = [
            expr,
            cmpr_exp1,
            cmpr_exp2,
            const_exp1,
            const_exp2,
            const_exp3,
            const_exp4,
        ]
        dfs = [
            expr,
            cmpr_exp1,
            const_exp1,
            const_exp2,
            cmpr_exp2,
            const_exp3,
            const_exp4,
        ]
        self.assertTrue(
            all(
                isinstance(exp, type(bfs[idx]))
                for idx, exp in enumerate(list(expr.walk()))
            )
        )
        self.assertTrue(
            all(
                isinstance(exp, type(dfs[idx]))
                for idx, exp in enumerate(list(expr.walk(bfs=False)))
            )
        )

    def test_find_all(self):
        const_exp1 = ConstantValueExpression(1)
        const_exp2 = ConstantValueExpression(1)
        const_exp3 = ConstantValueExpression(0)
        const_exp4 = ConstantValueExpression(5)

        cmpr_exp1 = ComparisonExpression(
            ExpressionType.COMPARE_GEQ, const_exp1, const_exp2
        )

        cmpr_exp2 = ComparisonExpression(
            ExpressionType.COMPARE_GEQ, const_exp3, const_exp4
        )

        expr = LogicalExpression(ExpressionType.LOGICAL_AND, cmpr_exp1, cmpr_exp2)

        self.assertEqual(
            [cmpr_exp1, cmpr_exp2],
            [exp for exp in list(expr.find_all(ComparisonExpression))],
        )
        self.assertNotEqual(
            [cmpr_exp2, cmpr_exp1],
            [exp for exp in list(expr.find_all(ComparisonExpression))],
        )

        self.assertNotEqual(
            [None],
            [exp for exp in list(expr.find_all(TupleValueExpression))],
        )

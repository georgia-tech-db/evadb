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
from eva.expression.arithmetic_expression import ArithmeticExpression
from eva.expression.constant_value_expression import ConstantValueExpression


class ArithmeticExpressionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_addition(self):
        const_exp1 = ConstantValueExpression(2)
        const_exp2 = ConstantValueExpression(5)

        cmpr_exp = ArithmeticExpression(
            ExpressionType.ARITHMETIC_ADD, const_exp1, const_exp2
        )

        self.assertEqual([7], cmpr_exp.evaluate(None).frames[0].tolist())

    def test_subtraction(self):
        const_exp1 = ConstantValueExpression(5)
        const_exp2 = ConstantValueExpression(2)

        cmpr_exp = ArithmeticExpression(
            ExpressionType.ARITHMETIC_SUBTRACT, const_exp1, const_exp2
        )

        self.assertEqual([3], cmpr_exp.evaluate(None).frames[0].tolist())

    def test_multiply(self):
        const_exp1 = ConstantValueExpression(3)
        const_exp2 = ConstantValueExpression(5)

        cmpr_exp = ArithmeticExpression(
            ExpressionType.ARITHMETIC_MULTIPLY, const_exp1, const_exp2
        )

        self.assertEqual([15], cmpr_exp.evaluate(None).frames[0].tolist())

    def test_divide(self):
        const_exp1 = ConstantValueExpression(5)
        const_exp2 = ConstantValueExpression(5)

        cmpr_exp = ArithmeticExpression(
            ExpressionType.ARITHMETIC_DIVIDE, const_exp1, const_exp2
        )

        self.assertEqual([1], cmpr_exp.evaluate(None).frames[0].tolist())

    def test_aaequality(self):
        const_exp1 = ConstantValueExpression(5)
        const_exp2 = ConstantValueExpression(15)

        cmpr_exp = ArithmeticExpression(
            ExpressionType.ARITHMETIC_DIVIDE, const_exp1, const_exp2
        )

        cmpr_exp2 = ArithmeticExpression(
            ExpressionType.ARITHMETIC_MULTIPLY, const_exp1, const_exp2
        )
        cmpr_exp3 = ArithmeticExpression(
            ExpressionType.ARITHMETIC_MULTIPLY, const_exp2, const_exp1
        )

        self.assertNotEqual(cmpr_exp, cmpr_exp2)
        self.assertNotEqual(cmpr_exp2, cmpr_exp3)

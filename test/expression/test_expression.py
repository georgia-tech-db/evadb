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
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.models.inference.base_prediction import BasePrediction


class ExpressionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_comparison_compare_equal(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL,
            tpl_exp,
            const_exp
        )
        # ToDo implement a generic tuple class
        # to fetch the tuple from table
        compare = type("compare", (BasePrediction,), {
            "value": 1,
            "__eq__": lambda s, x: s.value == x
        })
        tuple1 = [[compare()], 2, 3]
        self.assertEqual([True], cmpr_exp.evaluate(tuple1, None))

    def test_compare_doesnt_broadcast_when_rhs_is_list(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression([1])

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL,
            tpl_exp,
            const_exp
        )

        compare = type("compare", (), {"value": 1,
                                       "__eq__": lambda s, x: s.value == x})
        tuple1 = [[compare()], 2, 3]
        self.assertEqual([True], cmpr_exp.evaluate(tuple1, None))


if __name__ == '__main__':
    unittest.main()

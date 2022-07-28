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
from eva.expression.aggregation_expression import AggregationExpression
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.function_expression import FunctionExpression
from eva.expression.logical_expression import LogicalExpression
from eva.expression.tuple_value_expression import TupleValueExpression


class ExpressionEvaluationTest(unittest.TestCase):
    def test_if_expr_tree_is_equal(self):
        const_exp1 = ConstantValueExpression(0)
        const_exp2 = ConstantValueExpression(0)
        columnName1 = TupleValueExpression(col_name="DATA")
        columnName2 = TupleValueExpression(col_name="DATA")

        aggr_expr1 = AggregationExpression(
            ExpressionType.AGGREGATION_AVG, None, columnName1
        )
        aggr_expr2 = AggregationExpression(
            ExpressionType.AGGREGATION_AVG, None, columnName2
        )
        cmpr_exp1 = ComparisonExpression(
            ExpressionType.COMPARE_NEQ, aggr_expr1, const_exp1
        )
        cmpr_exp2 = ComparisonExpression(
            ExpressionType.COMPARE_NEQ, aggr_expr2, const_exp2
        )

        self.assertEqual(cmpr_exp1, cmpr_exp2)

    def test_should_return_false_for_unequal_expressions(self):
        const_exp1 = ConstantValueExpression(0)
        const_exp2 = ConstantValueExpression(1)
        func_expr = FunctionExpression(lambda x: x + 1, name="test")
        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_NEQ, const_exp1, const_exp2
        )
        tuple_expr = TupleValueExpression(col_name="id")
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_MAX, None, tuple_expr
        )
        logical_expr = LogicalExpression(ExpressionType.LOGICAL_OR, cmpr_exp, cmpr_exp)

        self.assertNotEqual(const_exp1, const_exp2)
        self.assertNotEqual(cmpr_exp, const_exp1)
        self.assertNotEqual(func_expr, cmpr_exp)
        self.assertNotEqual(tuple_expr, aggr_expr)
        self.assertNotEqual(aggr_expr, tuple_expr)
        self.assertNotEqual(tuple_expr, cmpr_exp)
        self.assertNotEqual(logical_expr, cmpr_exp)

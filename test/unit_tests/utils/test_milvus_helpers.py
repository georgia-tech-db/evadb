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
from evadb.catalog.catalog_type import ColumnType
from evadb.expression.abstract_expression import ExpressionType
from evadb.expression.arithmetic_expression import ArithmeticExpression
from evadb.expression.comparison_expression import ComparisonExpression
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.expression.logical_expression import LogicalExpression
from evadb.expression.tuple_value_expression import TupleValueExpression

from evadb.third_party.vector_stores.milvus import expression_to_milvus_expr


class MilvusHelpersTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_expression_to_milvus_expr(self):
        # simple comparison expression
        test_tuple_expression = TupleValueExpression(name="extra_data")
        test_num_constant_expression = ConstantValueExpression(value=3)
        test_str_constant_expression = ConstantValueExpression(
            value="test", v_type=ColumnType.TEXT
        )
        test_eq_comparison_expr = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL,
            test_tuple_expression,
            test_num_constant_expression,
        )
        test_leq_comparison_expr = ComparisonExpression(
            ExpressionType.COMPARE_LEQ,
            test_tuple_expression,
            test_num_constant_expression,
        )
        test_like_comparison_expr = ComparisonExpression(
            ExpressionType.COMPARE_LIKE,
            test_tuple_expression,
            test_str_constant_expression,
        )

        expected_eq_comparison_milvus_expr = "(extra_data == 3)"
        actual_eq_comparison_milvus_expr = expression_to_milvus_expr(
            test_eq_comparison_expr
        )
        self.assertEqual(
            expected_eq_comparison_milvus_expr, actual_eq_comparison_milvus_expr
        )

        expected_leq_comparison_milvus_expr = "(extra_data <= 3)"
        actual_leq_comparison_milvus_expr = expression_to_milvus_expr(
            test_leq_comparison_expr
        )
        self.assertEqual(
            expected_leq_comparison_milvus_expr, actual_leq_comparison_milvus_expr
        )

        expected_like_comparison_milvus_expr = '(extra_data LIKE "test")'
        actual_like_comparison_milvus_expr = expression_to_milvus_expr(
            test_like_comparison_expr
        )
        self.assertEqual(
            expected_like_comparison_milvus_expr, actual_like_comparison_milvus_expr
        )

        # logical expressions
        test_or_logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_OR, test_eq_comparison_expr, test_leq_comparison_expr
        )
        expected_or_logical_milvus_expr = "((extra_data == 3) or (extra_data <= 3))"
        actual_or_comparsion_milvus_expr = expression_to_milvus_expr(
            test_or_logical_expr
        )
        self.assertEqual(
            expected_or_logical_milvus_expr, actual_or_comparsion_milvus_expr
        )

        test_not_logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_NOT, test_eq_comparison_expr, None
        )
        expected_not_logical_milvus_expr = "(not (extra_data == 3))"
        actual_not_comparsion_milvus_expr = expression_to_milvus_expr(
            test_not_logical_expr
        )
        self.assertEqual(
            expected_not_logical_milvus_expr, actual_not_comparsion_milvus_expr
        )

        # Arithmetic expressions
        test_add_arithmetic_expr = ArithmeticExpression(
            ExpressionType.ARITHMETIC_ADD,
            test_tuple_expression,
            test_num_constant_expression,
        )
        expected_add_arithmetic_milvus_expr = "(extra_data + 3)"
        actual_add_arithmetic_milvus_expr = expression_to_milvus_expr(
            test_add_arithmetic_expr
        )
        self.assertEqual(
            expected_add_arithmetic_milvus_expr, actual_add_arithmetic_milvus_expr
        )

        # Complex expression
        test_complex_expr = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            test_not_logical_expr,
            ComparisonExpression(
                ExpressionType.COMPARE_NEQ,
                test_add_arithmetic_expr,
                test_num_constant_expression,
            ),
        )
        expected_complex_milvus_expr = (
            "((not (extra_data == 3)) or ((extra_data + 3) != 3))"
        )
        actual_complex_milvus_expr = expression_to_milvus_expr(test_complex_expr)
        self.assertEqual(expected_complex_milvus_expr, actual_complex_milvus_expr)

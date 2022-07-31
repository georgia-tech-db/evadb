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
from unittest.mock import Mock

from eva.expression.abstract_expression import ExpressionType
from eva.expression.arithmetic_expression import ArithmeticExpression
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.expression_utils import (
    conjuction_list_to_expression_tree,
    contains_single_column,
    extract_range_list_from_comparison_expr,
    extract_range_list_from_predicate,
    is_simple_predicate,
)
from eva.expression.logical_expression import LogicalExpression
from eva.expression.tuple_value_expression import TupleValueExpression


class ExpressionUtilsTest(unittest.TestCase):
    def gen_cmp_expr(
        self,
        val,
        expr_type=ExpressionType.COMPARE_GREATER,
        name="id",
        const_first=False,
    ):
        constexpr = ConstantValueExpression(val)
        colname = TupleValueExpression(col_name=name, col_alias=f"T.{name}")
        if const_first:
            return ComparisonExpression(expr_type, constexpr, colname)
        return ComparisonExpression(expr_type, colname, constexpr)

    def test_extract_range_list_from_comparison_expr(self):
        expr_types = [
            ExpressionType.COMPARE_NEQ,
            ExpressionType.COMPARE_EQUAL,
            ExpressionType.COMPARE_GREATER,
            ExpressionType.COMPARE_LESSER,
            ExpressionType.COMPARE_GEQ,
            ExpressionType.COMPARE_LEQ,
        ]
        results = []
        for expr_type in expr_types:
            cmpr_exp = self.gen_cmp_expr(10, expr_type, const_first=True)
            results.append(extract_range_list_from_comparison_expr(cmpr_exp, 0, 100))
        expected = [
            [(0, 9), (11, 100)],
            [(10, 10)],
            [(0, 9)],
            [(11, 100)],
            [(0, 10)],
            [(10, 100)],
        ]
        self.assertEqual(results, expected)

        results = []
        for expr_type in expr_types:
            cmpr_exp = self.gen_cmp_expr(10, expr_type)
            results.append(extract_range_list_from_comparison_expr(cmpr_exp, 0, 100))
        expected = [
            [(0, 9), (11, 100)],
            [(10, 10)],
            [(11, 100)],
            [(0, 9)],
            [(10, 100)],
            [(0, 10)],
        ]
        self.assertEqual(results, expected)

        with self.assertRaises(RuntimeError):
            cmpr_exp = LogicalExpression(ExpressionType.LOGICAL_AND, Mock(), Mock())
            extract_range_list_from_comparison_expr(cmpr_exp, 0, 100)

        with self.assertRaises(RuntimeError):
            cmpr_exp = self.gen_cmp_expr(10, ExpressionType.COMPARE_CONTAINS)
            extract_range_list_from_comparison_expr(cmpr_exp, 0, 100)
        with self.assertRaises(RuntimeError):
            cmpr_exp = self.gen_cmp_expr(10, ExpressionType.COMPARE_IS_CONTAINED)
            extract_range_list_from_comparison_expr(cmpr_exp, 0, 100)

    def test_extract_range_list_from_predicate(self):
        # id > 10 AND id > 20 -> (21, 100)
        expr = LogicalExpression(
            ExpressionType.LOGICAL_AND,
            self.gen_cmp_expr(10),
            self.gen_cmp_expr(20),
        )
        self.assertEqual(extract_range_list_from_predicate(expr, 0, 100), [(21, 100)])
        # id > 10 OR id > 20 -> (11, 100)
        expr = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            self.gen_cmp_expr(10),
            self.gen_cmp_expr(20),
        )
        self.assertEqual(extract_range_list_from_predicate(expr, 0, 100), [(11, 100)])

        # (id > 10 OR id > 20) OR (id > 10 AND id < 5) -> (11, 100)
        expr1 = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            self.gen_cmp_expr(10),
            self.gen_cmp_expr(20),
        )
        expr2 = LogicalExpression(
            ExpressionType.LOGICAL_AND,
            self.gen_cmp_expr(10),
            self.gen_cmp_expr(5, ExpressionType.COMPARE_LESSER),
        )
        expr = LogicalExpression(ExpressionType.LOGICAL_OR, expr1, expr2)
        self.assertEqual(extract_range_list_from_predicate(expr, 0, 100), [(11, 100)])

        # (id > 10 OR id > 20) AND (id > 10 AND id < 5) -> []
        expr = LogicalExpression(ExpressionType.LOGICAL_AND, expr1, expr2)
        self.assertEqual(extract_range_list_from_predicate(expr, 0, 100), [])

        # (id < 10 OR id > 20) OR (id > 25 OR id < 5) -> [(0,9), (21,100)]
        expr1 = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            self.gen_cmp_expr(10, ExpressionType.COMPARE_LESSER),
            self.gen_cmp_expr(20),
        )
        expr2 = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            self.gen_cmp_expr(25),
            self.gen_cmp_expr(5, ExpressionType.COMPARE_LESSER),
        )
        expr = LogicalExpression(ExpressionType.LOGICAL_OR, expr1, expr2)
        self.assertEqual(
            extract_range_list_from_predicate(expr, 0, 100),
            [(0, 9), (21, 100)],
        )

        with self.assertRaises(RuntimeError):
            expr = ArithmeticExpression(
                ExpressionType.AGGREGATION_COUNT, Mock(), Mock()
            )
            extract_range_list_from_predicate(expr, 0, 100)

    def test_predicate_contains_single_column(self):
        self.assertTrue(contains_single_column(self.gen_cmp_expr(10)))
        expr1 = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            self.gen_cmp_expr(10, ExpressionType.COMPARE_GREATER, "x"),
            self.gen_cmp_expr(10, ExpressionType.COMPARE_GREATER, "x"),
        )
        self.assertTrue(contains_single_column(expr1))
        expr2 = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            self.gen_cmp_expr(10, ExpressionType.COMPARE_GREATER, "x"),
            self.gen_cmp_expr(10, ExpressionType.COMPARE_GREATER, "y"),
        )
        self.assertFalse(contains_single_column(expr2))
        expr = LogicalExpression(ExpressionType.LOGICAL_OR, expr1, expr2)
        self.assertFalse(contains_single_column(expr))

    def test_is_simple_predicate(self):
        self.assertTrue(is_simple_predicate(self.gen_cmp_expr(10)))

        expr = ArithmeticExpression(ExpressionType.AGGREGATION_COUNT, Mock(), Mock())
        self.assertFalse(is_simple_predicate(expr))

        expr = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            self.gen_cmp_expr(10, ExpressionType.COMPARE_GREATER, "x"),
            self.gen_cmp_expr(10, ExpressionType.COMPARE_GREATER, "y"),
        )
        self.assertFalse(is_simple_predicate(expr))

    def test_conjuction_list_to_expression_tree(self):
        expr1 = self.gen_cmp_expr(10)
        expr2 = self.gen_cmp_expr(20)
        new_expr = conjuction_list_to_expression_tree([expr1, expr2])
        self.assertEqual(new_expr.etype, ExpressionType.LOGICAL_AND)
        self.assertEqual(new_expr.children[0], expr1)
        self.assertEqual(new_expr.children[1], expr2)

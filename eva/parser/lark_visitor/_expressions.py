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
import numpy as np
from lark import Tree

from eva.catalog.catalog_type import ColumnType
from eva.expression.abstract_expression import ExpressionType
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.logical_expression import LogicalExpression


##################################################################
# EXPRESSIONS
##################################################################
class Expressions:
    def string_literal(self, tree):
        text = tree.children[0]
        if text is not None:
            return ConstantValueExpression(text[1:-1], ColumnType.TEXT)
        else:
            return None

    def array_literal(self, tree):
        array_elements = []
        for child in tree.children:
            if isinstance(child, Tree):
                array_element = self.visit(child).value
                array_elements.append(array_element)

        res = ConstantValueExpression(np.array(array_elements), ColumnType.NDARRAY)
        return res

    def expression_atom(self, tree):
        output = self.visit_children(tree)
        # flatten
        output = output[0]
        return output

    def comparison_expression(self, tree):
        left = self.visit_children(tree.children[0])
        return left

    def constant(self, tree):
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "real_literal":
                    real_literal = self.visit(child)
                    return ConstantValueExpression(real_literal, ColumnType.FLOAT)
                elif child.data == "decimal_literal":
                    decimal_literal = self.visit(child)
                    return ConstantValueExpression(decimal_literal, ColumnType.INTEGER)

        return self.visit_children(tree)

    def logical_expression(self, tree):
        left = self.visit(tree.children[0])
        op = self.visit(tree.children[1])
        right = self.visit(tree.children[2])
        return LogicalExpression(op, left, right)

    def binary_comparison_predicate(self, tree):
        left = self.visit(tree.children[0])
        op = self.visit(tree.children[1])
        right = self.visit(tree.children[2])
        return ComparisonExpression(op, left, right)

    def nested_expression_atom(self, tree):
        # ToDo Can there be >1 expression in this case
        expr = tree.children[0]
        return self.visit(expr)

    def comparison_operator(self, tree):
        op = str(tree.children[0])

        if op == "=":
            return ExpressionType.COMPARE_EQUAL
        elif op == "<":
            return ExpressionType.COMPARE_LESSER
        elif op == ">":
            return ExpressionType.COMPARE_GREATER
        elif op == ">=":
            return ExpressionType.COMPARE_GEQ
        elif op == "<=":
            return ExpressionType.COMPARE_LEQ
        elif op == "!=":
            return ExpressionType.COMPARE_NEQ
        elif op == "@>":
            return ExpressionType.COMPARE_CONTAINS
        elif op == "<@":
            return ExpressionType.COMPARE_IS_CONTAINED
        else:
            return ExpressionType.INVALID

    def logical_operator(self, tree):
        op = str(tree.children[0])

        if op == "OR":
            return ExpressionType.LOGICAL_OR
        elif op == "AND":
            return ExpressionType.LOGICAL_AND
        else:
            return ExpressionType.INVALID

    def expressions_with_defaults(self, tree):
        expr_list = []
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "expression_or_default":
                    expression = self.visit(child)
                    expr_list.append(expression)
        return expr_list

    def sample_clause(self, tree):
        sample_list = self.visit_children(tree)
        assert len(sample_list) == 2
        return ConstantValueExpression(sample_list[1])

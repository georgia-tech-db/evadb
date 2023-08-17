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
import numpy as np
from lark import Tree

from evadb.catalog.catalog_type import ColumnType
from evadb.expression.abstract_expression import ExpressionType
from evadb.expression.comparison_expression import ComparisonExpression
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.expression.logical_expression import LogicalExpression


##################################################################
# EXPRESSIONS
##################################################################
class Expressions:
    def string_literal(self, tree):
        text = tree.children[0]
        assert text is not None
        return ConstantValueExpression(text[1:-1], ColumnType.TEXT)

    def array_literal(self, tree):
        array_elements = []
        for child in tree.children:
            if isinstance(child, Tree):
                array_element = self.visit(child).value
                array_elements.append(array_element)

        res = ConstantValueExpression(np.array(array_elements), ColumnType.NDARRAY)
        return res

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
        # Todo Can there be >1 expression in this case
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
        elif op == "LIKE":
            return ExpressionType.COMPARE_LIKE

    def logical_operator(self, tree):
        op = str(tree.children[0])

        if op == "OR":
            return ExpressionType.LOGICAL_OR
        elif op == "AND":
            return ExpressionType.LOGICAL_AND

    def expressions_with_defaults(self, tree):
        expr_list = []
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "expression_or_default":
                    expression = self.visit(child)
                    expr_list.append(expression)
        return expr_list

    def sample_params(self, tree):
        sample_type = None
        sample_freq = None
        for child in tree.children:
            if child.data == "sample_clause":
                sample_freq = self.visit(child)
            elif child.data == "sample_clause_with_type":
                sample_type, sample_freq = self.visit(child)
        return sample_type, sample_freq

    def sample_clause(self, tree):
        sample_list = self.visit_children(tree)
        assert len(sample_list) == 2
        return ConstantValueExpression(sample_list[1])

    def sample_clause_with_type(self, tree):
        sample_list = self.visit_children(tree)
        assert len(sample_list) == 3 or len(sample_list) == 2
        if len(sample_list) == 3:
            return ConstantValueExpression(sample_list[1]), ConstantValueExpression(
                sample_list[2]
            )
        else:
            return ConstantValueExpression(sample_list[1]), ConstantValueExpression(1)

    def chunk_params(self, tree):
        chunk_params = self.visit_children(tree)
        assert len(chunk_params) == 2 or len(chunk_params) == 4
        if len(chunk_params) == 4:
            return {
                "chunk_size": ConstantValueExpression(chunk_params[1]),
                "chunk_overlap": ConstantValueExpression(chunk_params[3]),
            }

        elif len(chunk_params) == 2:
            if chunk_params[0] == "CHUNK_SIZE":
                return {
                    "chunk_size": ConstantValueExpression(chunk_params[1]),
                }
            elif chunk_params[0] == "CHUNK_OVERLAP":
                return {
                    "chunk_overlap": ConstantValueExpression(chunk_params[1]),
                }
            else:
                assert f"incorrect keyword found {chunk_params[0]}"

    def colon_param_dict(self, tree):
        param_dict = {}
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "colon_param":
                    param = self.visit(child)
                    key = param[0].value
                    value = param[1].value
                    param_dict[key] = value
        return param_dict

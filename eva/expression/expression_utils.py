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
from typing import List

from eva.expression.abstract_expression import AbstractExpression, ExpressionType
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.expression.logical_expression import LogicalExpression
from eva.catalog.models.df_column import DataFrameColumn


def get_columns_in_predicate(expr: AbstractExpression) -> List[DataFrameColumn]:
    columns = []
    for child in expr.children:
        if isinstance(child, TupleValueExpression):
            columns.append(child.col_object)
        else:
            columns.extend(get_columns_in_predicate(child))
    return columns


def split_expr_tree_into_list_of_conjunct_exprs(expr: AbstractExpression) -> List[AbstractExpression]:
    """
    Split the input expr into a list of conjunctive sub-exprs.
    Eg:
        E1 -> [E1]
        E1 AND E2 AND E3 -> [E1, E2, E3]
        (E1 OR E2) AND E3 -> [E1 OR E2, E3]
    """
    if expr is None:
        return None
    conjunction_exprs = []
    if expr.etype == ExpressionType.LOGICAL_AND:
        conjunction_exprs.extend(
            split_expr_tree_into_list_of_conjunct_exprs(expr.children[0],
                                                        conjunction_exprs))
        conjunction_exprs.extend(
            split_expr_tree_into_list_of_conjunct_exprs(expr.children[1],
                                                        conjunction_exprs))
    else:
        conjunction_exprs.append(expr)

    return conjunction_exprs


def create_expr_tree_from_conjunct_exprs(self, conjunct_exprs: List[AbstractExpression]) -> AbstractExpression:
        """
                                 AND
                                /   \
        [ E1, E2, E3 ]  ->   AND     E3
                            /   \
                           E1    E2
        """
        # validate conjunct_exprs
        for expr in conjunct_exprs:
            if expr is not None:
                raise SystemError('expression should not be null')

        if len(conjunct_exprs) == 1:
            return conjunct_exprs.pop()

        right = conjunct_exprs.pop()
        left = self.combine_expr_list_using_conjunction(conjunct_exprs)
        root=LogicalExpression(ExpressionType.LOGICAL_AND, left, right)
        return root

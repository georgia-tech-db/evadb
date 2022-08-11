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

from typing import List, Set

from eva.expression.abstract_expression import AbstractExpression, ExpressionType
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.logical_expression import LogicalExpression
from eva.expression.tuple_value_expression import TupleValueExpression


def expression_tree_to_conjunction_list(expression_tree):
    expression_list = []
    if expression_tree.etype == ExpressionType.LOGICAL_AND:
        expression_list.extend(
            expression_tree_to_conjunction_list(expression_tree.children[0])
        )
        expression_list.extend(
            expression_tree_to_conjunction_list(expression_tree.children[1])
        )
    else:
        expression_list.append(expression_tree)

    return expression_list


def conjuction_list_to_expression_tree(
    expression_list: List[AbstractExpression],
) -> AbstractExpression:
    """Convert expression list to expression tree wuing conjuction connector

    Args:
        expression_list (List[AbstractExpression]): list of conjunctives

    Returns:
        AbstractExpression: expression tree
    """
    if len(expression_list) == 0:
        return None
    prev_expr = expression_list[0]
    for expr in expression_list[1:]:
        prev_expr = LogicalExpression(ExpressionType.LOGICAL_AND, prev_expr, expr)
    return prev_expr


def extract_range_list_from_comparison_expr(
    expr: ComparisonExpression, lower_bound: int, upper_bound: int
) -> List:
    """Extracts the valid range from the comparison expression.
    The expression needs to be amongst <, >, <=, >=, =, !=.

    Args:
        expr (ComparisonExpression): comparison expression with two children
            that are leaf expression nodes. If the input doesnot match,
            the function return False
        lower_bound (int): lower bound of the comparison predicate
        upper_bound (int): upper bound of the comparison predicate

    Returns:
        List[Tuple(int)]: list of valid ranges

    Raises:
        RuntimeError: Invalid expression

    Example:
        extract_range_from_comparison_expr(id < 10, 0, inf): True, [(0,9)]
    """

    if not isinstance(expr, ComparisonExpression):
        raise RuntimeError(f"Expected Comparision Expression, got {type(expr)}")
    left = expr.children[0]
    right = expr.children[1]
    expr_type = expr.etype
    val = None
    const_first = False
    if isinstance(left, TupleValueExpression) and isinstance(
        right, ConstantValueExpression
    ):
        val = right.value
    elif isinstance(left, ConstantValueExpression) and isinstance(
        right, TupleValueExpression
    ):
        val = left.value
        const_first = True
    else:
        raise RuntimeError(
            f"Only supports extracting range from Comparision Expression \
                with two children TupleValueExpression and \
                ConstantValueExpression, got {left} and {right}"
        )

    if const_first:
        if expr_type is ExpressionType.COMPARE_GREATER:
            expr_type = ExpressionType.COMPARE_LESSER
        elif expr_type is ExpressionType.COMPARE_LESSER:
            expr_type = ExpressionType.COMPARE_GREATER
        elif expr_type is ExpressionType.COMPARE_GEQ:
            expr_type = ExpressionType.COMPARE_LEQ
        elif expr_type is ExpressionType.COMPARE_LEQ:
            expr_type = ExpressionType.COMPARE_GEQ

    valid_ranges = []
    if expr_type == ExpressionType.COMPARE_EQUAL:
        valid_ranges.append((val, val))
    elif expr_type == ExpressionType.COMPARE_NEQ:
        valid_ranges.append((lower_bound, val - 1))
        valid_ranges.append((val + 1, upper_bound))
    elif expr_type == ExpressionType.COMPARE_GREATER:
        valid_ranges.append((val + 1, upper_bound))
    elif expr_type == ExpressionType.COMPARE_GEQ:
        valid_ranges.append((val, upper_bound))
    elif expr_type == ExpressionType.COMPARE_LESSER:
        valid_ranges.append((lower_bound, val - 1))
    elif expr_type == ExpressionType.COMPARE_LEQ:
        valid_ranges.append((lower_bound, val))
    else:
        raise RuntimeError(f"Unsupported Expression Type {expr_type}")
    return valid_ranges


def extract_range_list_from_predicate(
    predicate: AbstractExpression, lower_bound: int, upper_bound: int
) -> List:
    """The function converts the range predicate on the column in the
        `predicate` to a list of [(start_1, end_1), ... ] pairs.
        Assumes the predicate contains conditions on only one column

    Args:
        predicate (AbstractExpression): Input predicate to extract
            valid ranges. The predicate should contain conditions on
            only one columns, else it raise error.
        lower_bound (int): lower bound of the comparison predicate
        upper_bound (int): upper bound of the comparison predicate

    Returns:
        List[Tuple]: list of (start, end) pairs of valid ranges

    Example:
            id < 10 : [(0, 9)]
            id > 5 AND id < 10 : [(6, 9)]
            id < 10 OR id >20 : [(0, 9), (21, Inf)]
    """

    def overlap(x, y):
        overlap = (max(x[0], y[0]), min(x[1], y[1]))
        if overlap[0] <= overlap[1]:
            return overlap

    def union(ranges: List):
        # union all the ranges
        reduced_list = []
        for begin, end in sorted(ranges):
            if reduced_list and reduced_list[-1][1] >= begin - 1:
                reduced_list[-1] = (
                    reduced_list[-1][0],
                    max(reduced_list[-1][1], end),
                )
            else:
                reduced_list.append((begin, end))
        return reduced_list

    if predicate.etype == ExpressionType.LOGICAL_AND:
        left_ranges = extract_range_list_from_predicate(
            predicate.children[0], lower_bound, upper_bound
        )
        right_ranges = extract_range_list_from_predicate(
            predicate.children[1], lower_bound, upper_bound
        )
        valid_overlaps = []
        for left_range in left_ranges:
            for right_range in right_ranges:
                over = overlap(left_range, right_range)
                if over:
                    valid_overlaps.append(over)
        return union(valid_overlaps)

    elif predicate.etype == ExpressionType.LOGICAL_OR:
        left_ranges = extract_range_list_from_predicate(
            predicate.children[0], lower_bound, upper_bound
        )
        right_ranges = extract_range_list_from_predicate(
            predicate.children[1], lower_bound, upper_bound
        )
        return union(left_ranges + right_ranges)

    elif isinstance(predicate, ComparisonExpression):
        return union(
            extract_range_list_from_comparison_expr(predicate, lower_bound, upper_bound)
        )

    else:
        raise RuntimeError(f"Contains unsuporrted expression {type(predicate)}")


def get_columns_in_predicate(predicate: AbstractExpression) -> Set[str]:
    """Get columns accessed in the predicate

    Args:
        predicate (AbstractExpression): input predicate

    Returns:
        Set[str]: list of column aliases used in the predicate
    """
    if isinstance(predicate, TupleValueExpression):
        return set([predicate.col_alias])
    cols = set()
    for child in predicate.children:
        child_cols = get_columns_in_predicate(child)
        if len(child_cols):
            cols.update(child_cols)
    return cols


def contains_single_column(predicate: AbstractExpression, column: str = None) -> bool:
    """Checks if predicate contains conditions on single predicate

    Args:
        predicate (AbstractExpression): predicate expression
        column_alias (str): check if the single column matches
            the input column_alias
    Returns:
        bool: True, if contains single predicate, else False
            if predicate is None, return False
    """

    if not predicate:
        return False

    cols = get_columns_in_predicate(predicate)
    if len(cols) == 1:
        if column is None:
            return True
        pred_col = cols.pop()
        if pred_col == column:
            return True
    return False


def is_simple_predicate(predicate: AbstractExpression) -> bool:
    """Checks if conditions in the predicate are on a single column and
        only contains LogicalExpression, ComparisonExpression,
        TupleValueExpression or ConstantValueExpression

    Args:
        predicate (AbstractExpression): predicate expression to check

    Returns:
        bool: True, if it is a simple predicate, lese False
    """

    def _has_simple_expressions(expr):
        simple = type(expr) in simple_expressions
        for child in expr.children:
            simple = simple and _has_simple_expressions(child)
        return simple

    simple_expressions = [
        LogicalExpression,
        ComparisonExpression,
        TupleValueExpression,
        ConstantValueExpression,
    ]

    return _has_simple_expressions(predicate) and contains_single_column(predicate)

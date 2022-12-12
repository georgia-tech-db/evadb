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
from typing import List, Tuple

from eva.catalog.catalog_manager import CatalogManager
from eva.expression.abstract_expression import AbstractExpression, ExpressionType
from eva.expression.expression_utils import (
    conjuction_list_to_expression_tree,
    contains_single_column,
    expression_tree_to_conjunction_list,
    get_columns_in_predicate,
    is_simple_predicate,
)
from eva.parser.alias import Alias
from eva.parser.create_statement import ColumnDefinition
from eva.utils.logging_manager import logger


def column_definition_to_udf_io(col_list: List[ColumnDefinition], is_input: bool):
    """Create the UdfIO object fro each column definition provided

    Arguments:
        col_list(List[ColumnDefinition]): parsed input/output definitions
        is_input(bool): true if input else false
    """
    if isinstance(col_list, ColumnDefinition):
        col_list = [col_list]

    result_list = []
    for col in col_list:
        if col is None:
            logger.error("Empty column definition while creating udf io")
            result_list.append(col)
        result_list.append(
            CatalogManager().udf_io(
                col.name,
                col.type,
                array_type=col.array_type,
                dimensions=col.dimension,
                is_input=is_input,
            )
        )
    return result_list


def extract_equi_join_keys(
    join_predicate: AbstractExpression,
    left_table_aliases: List[str],
    right_table_aliases: List[str],
) -> Tuple[List[AbstractExpression], List[AbstractExpression]]:

    pred_list = expression_tree_to_conjunction_list(join_predicate)
    left_join_keys = []
    right_join_keys = []
    for pred in pred_list:
        if pred.etype == ExpressionType.COMPARE_EQUAL:
            left_child = pred.children[0]
            right_child = pred.children[1]
            # only extract if both are TupleValueExpression
            if (
                left_child.etype == ExpressionType.TUPLE_VALUE
                and right_child.etype == ExpressionType.TUPLE_VALUE
            ):
                if (
                    left_child.table_alias in left_table_aliases
                    and right_child.table_alias in right_table_aliases
                ):
                    left_join_keys.append(left_child)
                    right_join_keys.append(right_child)
                elif (
                    left_child.table_alias in right_table_aliases
                    and right_child.table_alias in left_table_aliases
                ):
                    left_join_keys.append(right_child)
                    right_join_keys.append(left_child)

    return (left_join_keys, right_join_keys)


def extract_pushdown_predicate(
    predicate: AbstractExpression, column_alias: str
) -> Tuple[AbstractExpression, AbstractExpression]:
    """Decompose the predicate into pushdown predicate and remaining predicate

    Args:
        predicate (AbstractExpression): predicate that needs to be decomposed
        column (str): column_alias to extract predicate
    Returns:
        Tuple[AbstractExpression, AbstractExpression]: (pushdown predicate,
        remaining predicate)
    """
    if predicate is None:
        return None, None

    if contains_single_column(predicate, column_alias):
        if is_simple_predicate(predicate):
            return predicate, None

    pushdown_preds = []
    rem_pred = []
    pred_list = expression_tree_to_conjunction_list(predicate)
    for pred in pred_list:
        if contains_single_column(pred, column_alias) and is_simple_predicate(pred):
            pushdown_preds.append(pred)
        else:
            rem_pred.append(pred)

    return (
        conjuction_list_to_expression_tree(pushdown_preds),
        conjuction_list_to_expression_tree(rem_pred),
    )


def extract_pushdown_predicate_for_alias(
    predicate: AbstractExpression, aliases: List[Alias]
):
    """Extract predicate that can be pushed down based on the input aliases.

    Atomic predicates on the table columns that are the subset of the input aliases are
    considered as candidates for pushdown.

    Args:
        predicate (AbstractExpression): input predicate
        aliases (List[str]): aliases for which predicate can be pushed
    """
    if predicate is None:
        return None, None

    pred_list = expression_tree_to_conjunction_list(predicate)
    pushdown_preds = []
    rem_pred = []
    aliases = [alias.alias_name for alias in aliases]
    for pred in pred_list:
        column_aliases = get_columns_in_predicate(pred)
        table_aliases = set([col.split(".")[0] for col in column_aliases])
        if table_aliases.issubset(set(aliases)):
            pushdown_preds.append(pred)
        else:
            rem_pred.append(pred)
    return (
        conjuction_list_to_expression_tree(pushdown_preds),
        conjuction_list_to_expression_tree(rem_pred),
    )

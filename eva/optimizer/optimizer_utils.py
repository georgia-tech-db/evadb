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

from eva.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from eva.catalog.models.udf_metadata_catalog import UdfMetadataCatalogEntry
from eva.constants import DEFAULT_FUNCTION_EXPRESSION_COST
from eva.expression.abstract_expression import AbstractExpression, ExpressionType
from eva.expression.expression_utils import (
    conjunction_list_to_expression_tree,
    contains_single_column,
    get_columns_in_predicate,
    is_simple_predicate,
    to_conjunction_list,
)
from eva.expression.function_expression import FunctionExpression
from eva.parser.alias import Alias
from eva.parser.create_statement import ColumnDefinition
from eva.utils.logging_manager import logger


def column_definition_to_udf_io(col_list: List[ColumnDefinition], is_input: bool):
    """Create the UdfIOCatalogEntry object fro each column definition provided

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
            UdfIOCatalogEntry(
                col.name,
                col.type,
                col.cci.nullable,
                array_type=col.array_type,
                array_dimensions=col.dimension,
                is_input=is_input,
            )
        )
    return result_list


def metadata_definition_to_udf_metadata(metadata_list: List[Tuple[str, str]]):
    """Create the UdfMetadataCatalogEntry object for each metadata definition provided

    Arguments:
        col_list(List[Tuple[str, str]]): parsed metadata definitions
    """
    result_list = []
    for metadata in metadata_list:
        result_list.append(
            UdfMetadataCatalogEntry(
                metadata[0],
                metadata[1],
            )
        )
    return result_list


def extract_equi_join_keys(
    join_predicate: AbstractExpression,
    left_table_aliases: List[str],
    right_table_aliases: List[str],
) -> Tuple[List[AbstractExpression], List[AbstractExpression]]:
    pred_list = to_conjunction_list(join_predicate)
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
    pred_list = to_conjunction_list(predicate)
    for pred in pred_list:
        if contains_single_column(pred, column_alias) and is_simple_predicate(pred):
            pushdown_preds.append(pred)
        else:
            rem_pred.append(pred)

    return (
        conjunction_list_to_expression_tree(pushdown_preds),
        conjunction_list_to_expression_tree(rem_pred),
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

    pred_list = to_conjunction_list(predicate)
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
        conjunction_list_to_expression_tree(pushdown_preds),
        conjunction_list_to_expression_tree(rem_pred),
    )


def get_func_expression_execution_cost(expr: FunctionExpression) -> float:
    """
    This function computes the estimated cost of executing a given function expression
    based on the statistics in the catalog. If no statistics are available, it assumes
    a default cost, DEFAULT_FUNCTION_EXPRESSION_COST. If the function expression is
    nested, it computes the total cost including all the child function expressions.

    Args:
        expr (FunctionExpression): The FunctionExpression object whose cost needs to be
        computed.

    Returns:
        float: The estimated cost of executing the function expression.
    """
    total_cost = 0
    # iterate over all the function expression and accumulate the cost
    for child_expr in expr.find_all(FunctionExpression):
        cost_entry = CatalogManager().get_udf_cost_catalog_entry(child_expr.name)
        if cost_entry:
            total_cost += cost_entry.cost
        else:
            total_cost += DEFAULT_FUNCTION_EXPRESSION_COST
    return total_cost

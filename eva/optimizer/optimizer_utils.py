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

from typing import List, Tuple
from eva.expression.abstract_expression import (AbstractExpression,
                                                ExpressionType)
from eva.expression.expression_utils import expression_tree_to_conjunction_list
from eva.catalog.catalog_manager import CatalogManager
from eva.parser.create_statement import ColumnDefinition
from eva.utils.logging_manager import logger
from eva.parser.table_ref import TableInfo


def column_definition_to_udf_io(
        col_list: List[ColumnDefinition], is_input: bool):
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
            logger.error(
                "Empty column definition while creating udf io")
            result_list.append(col)
        result_list.append(
            CatalogManager().udf_io(col.name, col.type,
                                    array_type=col.array_type,
                                    dimensions=col.dimension,
                                    is_input=is_input)
        )
    return result_list


def extract_equi_join_keys(join_predicate: AbstractExpression,
                           left_table_aliases: List[str],
                           right_table_aliases: List[str]) \
    -> Tuple[List[AbstractExpression],
             List[AbstractExpression]]:

    pred_list = expression_tree_to_conjunction_list(join_predicate)
    left_join_keys = []
    right_join_keys = []
    for pred in pred_list:
        if pred.etype == ExpressionType.COMPARE_EQUAL:
            left_child = pred.children[0]
            right_child = pred.children[1]
            # only extract if both are TupleValueExpression
            if (left_child.etype == ExpressionType.TUPLE_VALUE
                    and right_child.etype == ExpressionType.TUPLE_VALUE):
                if (left_child.table_alias in left_table_aliases
                        and right_child.table_alias in right_table_aliases):
                    left_join_keys.append(left_child)
                    right_join_keys.append(right_child)
                elif (left_child.table_alias in right_table_aliases
                        and right_child.table_alias in left_table_aliases):
                    left_join_keys.append(right_child)
                    right_join_keys.append(left_child)

    return (left_join_keys, right_join_keys)


def bind_table_ref(video_info: TableInfo) -> int:
    """Grab the metadata id from the catalog for
    input video
    Arguments:
        video_info {TableInfo} -- [input parsed video info]
    Return:
        catalog_entry for input table
    """

    catalog = CatalogManager()
    catalog_entry_id = catalog._dataset_service.dataset_by_name(
        video_info.table_name)
    return catalog_entry_id

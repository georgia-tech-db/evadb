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
from __future__ import annotations

import re
from typing import TYPE_CHECKING, List

from eva.catalog.catalog_type import TableType
from eva.catalog.catalog_utils import is_video_table
from eva.catalog.sql_config import IDENTIFIER_COLUMN
from eva.expression.function_expression import FunctionExpression
from eva.parser.select_statement import SelectStatement

if TYPE_CHECKING:
    from eva.binder.statement_binder_context import StatementBinderContext

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.table_ref import AVTableRef, ImageTableRef, TableInfo, TableRef
from eva.utils.logging_manager import logger


class BinderError(Exception):
    pass


def bind_table_info(table_info: TableInfo) -> TableCatalogEntry:
    """
    Uses catalog to bind the table information .

    Arguments:
         table_info (TableInfo): table information obtained from SQL query

    Returns:
        TableCatalogEntry  -  corresponding table catalog entry for the input table info
    """
    catalog = CatalogManager()
    obj = catalog.get_table_catalog_entry(
        table_info.table_name,
        table_info.database_name,
    )

    # Users should not be allowed to directly access or modify the SYSTEM tables, as
    # doing so can lead to the corruption of other tables. These tables include
    # metadata tables associated with unstructured data, such as the list of video
    # files in the video table. Protecting these tables is crucial in order to maintain
    # the integrity of the system.
    if obj and obj.table_type == TableType.SYSTEM_STRUCTURED_DATA:
        err_msg = (
            "The query attempted to access or modify the internal table"
            f"{table_info.table_name} of the system, but permission was denied."
        )
        logger.error(err_msg)
        raise BinderError(err_msg)

    if obj:
        table_info.table_obj = obj
    else:
        error = "{} does not exist. Create the table using" " CREATE TABLE.".format(
            table_info.table_name
        )
        logger.error(error)
        raise BinderError(error)


def extend_star(
    binder_context: StatementBinderContext,
) -> List[TupleValueExpression]:
    col_objs = binder_context._get_all_alias_and_col_name()

    target_list = list(
        [
            TupleValueExpression(col_name=col_name, table_alias=alias)
            for alias, col_name in col_objs
            if col_name != IDENTIFIER_COLUMN
        ]
    )
    return target_list


def check_groupby_pattern(groupby_string: str) -> None:
    # match the pattern of group by clause (e.g., 16f or 8s)
    pattern = re.search(r"^\d+[fs]$", groupby_string)
    # if valid pattern
    if not pattern:
        err_msg = "Incorrect GROUP BY pattern: {}".format(groupby_string)
        raise BinderError(err_msg)
    match_string = pattern.group(0)
    if not match_string[-1] == "f":
        err_msg = "Only grouping by frames (f) is supported"
        raise BinderError(err_msg)
    # TODO ACTION condition on segment length?


def check_table_object_is_video(table_ref: TableRef) -> None:
    if not is_video_table(table_ref.table.table_obj):
        err_msg = "GROUP BY only supported for video tables"
        raise BinderError(err_msg)


def get_table_ref_subclass(table_ref: TableRef) -> TableRef:
    if table_ref.is_table_atom():
        if table_ref.table.table_obj.table_type == TableType.VIDEO_DATA:
            return AVTableRef(table_ref)
        elif table_ref.table.table_obj.table_type == TableType.IMAGE_DATA:
            return ImageTableRef(table_ref)
    elif table_ref.is_join():
        table_ref.join_node.left = get_table_ref_subclass(table_ref.join_node.left)
        table_ref.join_node.right = get_table_ref_subclass(table_ref.join_node.right)

    return table_ref


def set_audio_video_tuple_flags(node: SelectStatement):
    if node.from_table.is_table_atom():
        has_audio_tuple = False
        has_video_tuple = False
        if node.target_list:
            for expr in node.target_list:
                if isinstance(expr, FunctionExpression):
                    for child in expr.children:
                        if isinstance(child, TupleValueExpression):
                            has_audio_tuple = (
                                has_audio_tuple or child.col_object.name == "audio"
                            )
                            has_video_tuple = (
                                has_video_tuple or child.col_object.name == "data"
                            )
        node.from_table.get_audio = has_audio_tuple
        node.from_table.get_video = has_video_tuple
    elif node.from_table.is_join():
        left = node.from_table.join_node.left
        right = node.from_table.join_node.right
        if isinstance(left, AVTableRef) and right.is_table_valued_expr():
            for child in right.table_valued_expr.func_expr.children:
                has_audio_tuple = False
                has_video_tuple = False
                if isinstance(child, TupleValueExpression):
                    has_audio_tuple = (
                        has_audio_tuple or child.col_object.name == "audio"
                    )
                    has_video_tuple = has_video_tuple or child.col_object.name == "data"
                left.get_audio = has_audio_tuple
                left.get_video = has_video_tuple
        elif isinstance(right, AVTableRef) and left.is_table_valued_expr():
            for child in left.table_valued_expr.func_expr.children:
                has_audio_tuple = False
                has_video_tuple = False
                if isinstance(child, TupleValueExpression):
                    has_audio_tuple = (
                        has_audio_tuple or child.col_object.name == "audio"
                    )
                    has_video_tuple = has_video_tuple or child.col_object.name == "data"
                right.get_audio = has_audio_tuple
                right.get_video = has_video_tuple

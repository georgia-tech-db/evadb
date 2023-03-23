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
    """
    Changes the table_ref object to the appropriate
    child class based on the type of table being queried

    Arguments:
         table_ref (TableRef): the original table_ref object
         from the statement being bound

    Returns:
        TableRef -  the child table ref object if table being
        queried has video/image else the original object
    """
    if table_ref.is_table_atom():
        if table_ref.table.table_obj.table_type == TableType.VIDEO_DATA:
            return AVTableRef(table_ref)
        elif table_ref.table.table_obj.table_type == TableType.IMAGE_DATA:
            return ImageTableRef(table_ref)
    elif table_ref.is_join():
        table_ref.join_node.left = get_table_ref_subclass(table_ref.join_node.left)
        table_ref.join_node.right = get_table_ref_subclass(table_ref.join_node.right)

    return table_ref


def set_av_table_ref_flags(node: SelectStatement):
    """
    Sets the has_audio/has_video flags for the AVTableRef object,
    if present in the select statement

    Arguments:
         node (SelectStatement): the select statement being bound
    """

    # For simple queries like SELECT UDF(..) FROM Table,
    # go over the tuples passed as arguments to the UDF
    if node.from_table.is_table_atom():
        if node.target_list:
            for expr in node.target_list:
                set_av_table_ref_flags_from_func_expr(node.from_table, expr)
    # For join based queries like SELECT * FROM Table JOIN LATERAL UDF(..),
    # go over the tuples passed as arguments to the UDF present on either side of the join
    elif node.from_table.is_join():
        left = node.from_table.join_node.left
        right = node.from_table.join_node.right
        # if the table to the left of the join is a video table and there is a UDF on the right
        if isinstance(left, AVTableRef) and right.is_table_valued_expr():
            set_av_table_ref_flags_from_func_expr(
                left, right.table_valued_expr.func_expr
            )
        # if the table to the right of the join is a video table and there is a UDF on the left
        elif isinstance(right, AVTableRef) and left.is_table_valued_expr():
            set_av_table_ref_flags_from_func_expr(
                right, left.table_valued_expr.func_expr
            )


def set_av_table_ref_flags_from_func_expr(
    table_ref: TableRef, func_expr: FunctionExpression
):
    """
    Helper method to set the has_audio/has_video flags for the AVTableRef object,
    if the func_expr uses audio/video columns

    Arguments:
         table_ref (TableRef): the table_ref of the statement being bound
         func_expr (FunctionExpression): the func_expr from the statement being bound
    """
    if not isinstance(table_ref, AVTableRef):
        return
    for expr in func_expr.find_all(TupleValueExpression):
        if expr.col_object.name == "audio":
            table_ref.get_audio = True
        if expr.col_object.name == "data":
            table_ref.get_video = True

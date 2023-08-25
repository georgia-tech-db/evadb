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
from __future__ import annotations

import re
from typing import TYPE_CHECKING, List

from evadb.catalog.catalog_type import ColumnType, TableType
from evadb.catalog.catalog_utils import (
    get_video_table_column_definitions,
    is_document_table,
    is_pdf_table,
    is_string_col,
    is_video_table,
)
from evadb.catalog.models.column_catalog import ColumnCatalogEntry
from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.catalog.sql_config import IDENTIFIER_COLUMN

if TYPE_CHECKING:
    from evadb.binder.statement_binder_context import StatementBinderContext
    from evadb.catalog.catalog_manager import CatalogManager
from evadb.expression.abstract_expression import AbstractExpression, ExpressionType
from evadb.expression.function_expression import FunctionExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.alias import Alias
from evadb.parser.create_statement import ColumnDefinition
from evadb.parser.table_ref import TableInfo, TableRef
from evadb.third_party.databases.interface import get_database_handler
from evadb.utils.logging_manager import logger


class BinderError(Exception):
    pass


def check_data_source_and_table_are_valid(
    catalog: CatalogManager, database_name: str, table_name: str
):
    """
    Validate the database is valid and the requested table in database is
    also valid.
    """
    db_catalog_entry = catalog.get_database_catalog_entry(database_name)

    if db_catalog_entry is not None:
        handler = get_database_handler(
            db_catalog_entry.engine, **db_catalog_entry.params
        )
        handler.connect()

        # Get table definition.
        resp = handler.get_tables()
        if resp.error is not None:
            error = "There is no table in data source {}. Create the table using native query.".format(
                database_name,
            )
            logger.error(error)
            raise BinderError(error)

        # Check table existance.
        table_df = resp.data
        if table_name not in table_df["table_name"].values:
            error = "Table {} does not exist in data source {}. Create the table using native query.".format(
                table_name,
                database_name,
            )
            logger.error(error)
            raise BinderError(error)
    else:
        error = "{} data source does not exist. Create the new database source using CREATE DATABASE.".format(
            database_name,
        )
        logger.error(error)
        raise BinderError(error)


def create_table_catalog_entry_for_data_source(
    table_name: str, column_name_list: List[str]
):
    column_list = []
    for column_name in column_name_list:
        column_list.append(ColumnCatalogEntry(column_name, ColumnType.ANY))

    # Assemble table.
    table_catalog_entry = TableCatalogEntry(
        name=table_name,
        file_url=None,
        table_type=TableType.NATIVE_DATA,
        columns=column_list,
    )
    return table_catalog_entry


def bind_table_info(catalog: CatalogManager, table_info: TableInfo):
    """
    Uses catalog to bind the table information .

    Arguments:
         catalog (CatalogManager): catalog manager to use
         table_info (TableInfo): table information obtained from SQL query

    Returns:
        TableCatalogEntry  -  corresponding table catalog entry for the input table info
    """
    if table_info.database_name is not None:
        bind_native_table_info(catalog, table_info)
    else:
        bind_evadb_table_info(catalog, table_info)


def bind_native_table_info(catalog: CatalogManager, table_info: TableInfo):
    check_data_source_and_table_are_valid(
        catalog, table_info.database_name, table_info.table_name
    )

    db_catalog_entry = catalog.get_database_catalog_entry(table_info.database_name)
    handler = get_database_handler(db_catalog_entry.engine, **db_catalog_entry.params)
    handler.connect()

    # Assemble columns.
    column_df = handler.get_columns(table_info.table_name).data
    table_info.table_obj = create_table_catalog_entry_for_data_source(
        table_info.table_name, list(column_df["column_name"])
    )


def bind_evadb_table_info(catalog: CatalogManager, table_info: TableInfo):
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
            TupleValueExpression(name=col_name, table_alias=alias)
            for alias, col_name in col_objs
        ]
    )
    return target_list


def check_groupby_pattern(table_ref: TableRef, groupby_string: str) -> None:
    # match the pattern of group by clause (e.g., 16 frames or 8 samples)
    pattern = re.search(r"^\d+\s*(?:frames|samples|paragraphs)$", groupby_string)
    # if valid pattern
    if not pattern:
        err_msg = "Incorrect GROUP BY pattern: {}".format(groupby_string)
        raise BinderError(err_msg)
    match_string = pattern.group(0)
    suffix_string = re.sub(r"^\d+\s*", "", match_string)

    if suffix_string not in ["frames", "samples", "paragraphs"]:
        err_msg = "Grouping only supported by frames for videos, by samples for audio, and by paragraphs for documents"
        raise BinderError(err_msg)

    if suffix_string == "frames" and not is_video_table(table_ref.table.table_obj):
        err_msg = "Grouping by frames only supported for videos"
        raise BinderError(err_msg)

    if suffix_string == "samples" and not is_video_table(table_ref.table.table_obj):
        err_msg = "Grouping by samples only supported for videos"
        raise BinderError(err_msg)

    if suffix_string == "paragraphs" and not is_pdf_table(table_ref.table.table_obj):
        err_msg = "Grouping by paragraphs only supported for pdf tables"
        raise BinderError(err_msg)

    # TODO ACTION condition on segment length?


def check_table_object_is_groupable(table_ref: TableRef) -> None:
    table_obj = table_ref.table.table_obj

    if not (
        is_video_table(table_obj)
        or is_document_table(table_obj)
        or is_pdf_table(table_obj)
    ):
        raise BinderError("GROUP BY only supported for video and document tables")


def check_column_name_is_string(col_ref) -> None:
    if not is_string_col(col_ref.col_object):
        err_msg = "LIKE only supported for string columns"
        raise BinderError(err_msg)


def resolve_alias_table_value_expression(node: FunctionExpression):
    default_alias_name = node.name.lower()
    default_output_col_aliases = [str(obj.name.lower()) for obj in node.output_objs]
    if not node.alias:
        node.alias = Alias(default_alias_name, default_output_col_aliases)
    else:
        if not len(node.alias.col_names):
            node.alias = Alias(node.alias.alias_name, default_output_col_aliases)
        else:
            output_aliases = [
                str(col_name.lower()) for col_name in node.alias.col_names
            ]
            node.alias = Alias(node.alias.alias_name, output_aliases)

    assert len(node.alias.col_names) == len(
        node.output_objs
    ), f"""Expected {len(node.output_objs)} output columns for {node.alias.alias_name}, got {len(node.alias.col_names)}."""


def handle_bind_extract_object_function(
    node: FunctionExpression, binder_context: StatementBinderContext
):
    """Handles the binding of extract_object function.
        1. Bind the source video data
        2. Create and bind the detector function expression using the provided name.
        3. Create and bind the tracker function expression.
            Its inputs are id, data, output of detector.
        4. Bind the EXTRACT_OBJECT function expression and append the new children.
        5. Handle the alias and populate the outputs of the EXTRACT_OBJECT function

    Args:
        node (FunctionExpression): The function expression representing the extract object operation.
        binder_context (StatementBinderContext): The context object used to bind expressions in the statement.

    Raises:
        AssertionError: If the number of children in the `node` is not equal to 3.
    """
    assert (
        len(node.children) == 3
    ), f"Invalid arguments provided to {node}. Example correct usage, (data, Detector, Tracker)"

    # 1. Bind the source video
    video_data = node.children[0]
    binder_context.bind(video_data)

    # 2. Construct the detector
    # convert detector to FunctionExpression before binding
    # eg. YoloV5 -> YoloV5(data)
    detector = FunctionExpression(None, node.children[1].name)
    detector.append_child(video_data.copy())
    binder_context.bind(detector)

    # 3. Construct the tracker
    # convert tracker to FunctionExpression before binding
    # eg. ByteTracker -> ByteTracker(id, data, labels, bboxes, scores)
    tracker = FunctionExpression(None, node.children[2].name)
    # create the video id expression
    columns = get_video_table_column_definitions()
    tracker.append_child(
        TupleValueExpression(name=columns[1].name, table_alias=video_data.table_alias)
    )
    tracker.append_child(video_data.copy())
    binder_context.bind(tracker)
    # append the bound output of detector
    for obj in detector.output_objs:
        col_alias = "{}.{}".format(obj.udf_name.lower(), obj.name.lower())
        child = TupleValueExpression(
            obj.name,
            table_alias=obj.udf_name.lower(),
            col_object=obj,
            col_alias=col_alias,
        )
        tracker.append_child(child)

    # 4. Bind the EXTRACT_OBJECT expression and append the new children.
    node.children = []
    node.children = [video_data, detector, tracker]

    # 5. assign the outputs of tracker to the output of extract_object
    node.output_objs = tracker.output_objs
    node.projection_columns = [obj.name.lower() for obj in node.output_objs]

    # 5. resolve alias based on the what user provided
    # we assign the alias to tracker as it governs the output of the extract object
    resolve_alias_table_value_expression(node)
    tracker.alias = node.alias


def get_column_definition_from_select_target_list(
    target_list: List[AbstractExpression],
) -> List[ColumnDefinition]:
    """
    This function is used by CREATE TABLE AS (SELECT...) and
    CREATE UDF FROM (SELECT ...) to get the output objs from the
    child SELECT statement.
    """
    binded_col_list = []
    for expr in target_list:
        output_objs = (
            [(expr.name, expr.col_object)]
            if expr.etype == ExpressionType.TUPLE_VALUE
            else zip(expr.projection_columns, expr.output_objs)
        )
        for col_name, output_obj in output_objs:
            binded_col_list.append(
                ColumnDefinition(
                    col_name,
                    output_obj.type,
                    output_obj.array_type,
                    output_obj.array_dimensions,
                )
            )
    return binded_col_list


def drop_row_id_from_target_list(
    target_list: List[AbstractExpression],
) -> List[AbstractExpression]:
    """
    This function is intended to be used by CREATE UDF FROM (SELECT * FROM ...) and CREATE TABLE AS SELECT * FROM ... to exclude the row_id column.
    """
    filtered_list = []
    for expr in target_list:
        if isinstance(expr, TupleValueExpression):
            if expr.name == IDENTIFIER_COLUMN:
                continue
        filtered_list.append(expr)
    return filtered_list

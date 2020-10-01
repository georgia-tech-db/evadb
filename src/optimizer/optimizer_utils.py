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
from src.catalog.models.df_metadata import DataFrameMetadata
from src.expression.function_expression import FunctionExpression
from src.parser.table_ref import TableInfo
from src.catalog.catalog_manager import CatalogManager
from src.catalog.column_type import ColumnType
from typing import List

from src.expression.abstract_expression import AbstractExpression
from src.expression.tuple_value_expression import ExpressionType, \
    TupleValueExpression

from src.parser.create_statement import ColumnDefinition, \
    ColConstraintInfo
from src.parser.types import ParserColumnDataType
from src.utils.generic_utils import path_to_class, generate_file_path

from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager


def bind_dataset(video_info: TableInfo) -> DataFrameMetadata:
    """
    Uses catalog to bind the dataset information for given video string.

    Arguments:
         video_info (TableInfo): video information obtained in SQL query

    Returns:
        DataFrameMetadata  -  corresponding metadata for the input table info
    """
    catalog = CatalogManager()
    return catalog.get_dataset_metadata(video_info.database_name,
                                        video_info.table_name)


def bind_table_ref(video_info: TableInfo) -> int:
    """Grab the metadata id from the catalog for
    input video

    Arguments:
        video_info {TableInfo} -- [input parsed video info]
    Return:
        catalog_entry for input table
    """

    catalog = CatalogManager()
    catalog_entry_id, _ = catalog.get_table_bindings(video_info.database_name,
                                                     video_info.table_name,
                                                     None)
    return catalog_entry_id


def bind_columns_expr(target_columns: List[AbstractExpression],
                      column_mapping):
    if target_columns is None:
        return

    for column_exp in target_columns:
        child_count = column_exp.get_children_count()
        for i in range(child_count):
            bind_columns_expr([column_exp.get_child(i)], column_mapping)

        if column_exp.etype == ExpressionType.TUPLE_VALUE:
            bind_tuple_value_expr(column_exp, column_mapping)
        if column_exp.etype == ExpressionType.FUNCTION_EXPRESSION:
            bind_function_expr(column_exp, column_mapping)


def bind_tuple_value_expr(expr: TupleValueExpression, column_mapping):
    if not column_mapping:
        # TODO: Remove this and bring uniform interface throughout the system.
        _old_bind_tuple_value_expr(expr)
        return

    expr.col_object = column_mapping.get(expr.col_name.lower(), None)


def _old_bind_tuple_value_expr(expr):
    """
    NOTE: No tests for this  should be combined with latest interface
    """
    catalog = CatalogManager()
    table_id, column_ids = catalog.get_table_bindings(None,
                                                      expr.table_name,
                                                      [expr.col_name])
    expr.table_metadata_id = table_id
    if not isinstance(column_ids, list) or len(column_ids) == 0:
        LoggingManager().log(
            "Optimizer Utils:: bind_tuple_expr: \
            Cannot bind column name provided", LoggingLevel.ERROR)
    expr.col_metadata_id = column_ids.pop()


def bind_predicate_expr(predicate: AbstractExpression, column_mapping):
    # This function will be expanded as we add support for
    # complex predicate expressions and sub select predicates

    child_count = predicate.get_children_count()
    for i in range(child_count):
        bind_predicate_expr(predicate.get_child(i), column_mapping)

    if predicate.etype == ExpressionType.TUPLE_VALUE:
        bind_tuple_value_expr(predicate, column_mapping)

    if predicate.etype == ExpressionType.FUNCTION_EXPRESSION:
        bind_function_expr(predicate, column_mapping)


def bind_function_expr(expr: FunctionExpression, column_mapping):
    catalog = CatalogManager()
    udf_obj = catalog.get_udf_by_name(expr.name)
    # bind if the user queried a physical functional expression
    if udf_obj:
        if expr.output:
            expr.output_obj = catalog.get_udf_io_by_name(expr.output)
            if expr.output_obj is None:
                LoggingManager().log(
                    'Invalid output {} selected for UDF {}'.format(
                        expr.output, expr.name), LoggingLevel().ERROR)
        expr.function = path_to_class(udf_obj.impl_file_path,
                                  udf_obj.name)()
    

def create_column_metadata(col_list: List[ColumnDefinition]):
    """Create column metadata for the input parsed column list. This function
    will not commit the provided column into catalog table.
    Will only return in memory list of ColumnDataframe objects

    Arguments:
        col_list {List[ColumnDefinition]} -- parsed col list to be created
    """
    if isinstance(col_list, ColumnDefinition):
        col_list = [col_list]

    result_list = []
    for col in col_list:
        if col is None:
            LoggingManager().log(
                "Empty column while creating column metadata",
                LoggingLevel.ERROR)
            result_list.append(col)
        col_type = xform_parser_column_type_to_catalog_type(col.type)
        result_list.append(
            CatalogManager().create_column_metadata(
                col.name, col_type, col.dimension))

    return result_list


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
            LoggingManager().log(
                "Empty column definition while creating udf io",
                LoggingLevel.ERROR)
            result_list.append(col)
        col_type = xform_parser_column_type_to_catalog_type(col.type)
        result_list.append(
            CatalogManager().udf_io(col.name, col_type,
                                    col.dimension, is_input)
        )
    return result_list


def create_video_metadata(name: str) -> DataFrameMetadata:
    """Create video metadata object.
        We have predefined columns for such a object
        id:  the frame id
        data: the frame data

    Arguments:
        name (str): name of the metadata to be added to the catalog

    Returns:
        DataFrameMetadata:  corresponding metadata for the input table info
    """
    catalog = CatalogManager()
    columns = [ColumnDefinition('id', ParserColumnDataType.INTEGER, [],
                                ColConstraintInfo(unique=True))]
    # the ndarray dimensions are set as None. We need to fix this as we
    # cannot assume. Either ask the user to provide this with load or
    # we infer this from the provided video.
    columns.append(
        ColumnDefinition(
            'data', ParserColumnDataType.NDARRAY, [
                None, None, None]))
    col_metadata = create_column_metadata(columns)
    uri = str(generate_file_path(name))
    metadata = catalog.create_metadata(
        name, uri, col_metadata, identifier_column='id')
    return metadata


def xform_parser_column_type_to_catalog_type(
        col_type: ParserColumnDataType) -> ColumnType:
    """translate parser defined column type to the catalog type

    Arguments:
        col_type {ParserColumnDataType} -- input parser column type

    Returns:
        ColumnType -- catalog column type
    """
    if col_type == ParserColumnDataType.BOOLEAN:
        return ColumnType.BOOLEAN
    elif col_type == ParserColumnDataType.FLOAT:
        return ColumnType.FLOAT
    elif col_type == ParserColumnDataType.INTEGER:
        return ColumnType.INTEGER
    elif col_type == ParserColumnDataType.TEXT:
        return ColumnType.TEXT
    elif col_type == ParserColumnDataType.NDARRAY:
        return ColumnType.NDARRAY

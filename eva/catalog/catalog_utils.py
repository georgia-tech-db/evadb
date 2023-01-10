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
from typing import List

from eva.catalog.catalog_type import ColumnType, NdArrayType, TableType
from eva.catalog.models.column_catalog import ColumnCatalogEntry
from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.catalog.models.udf_cache_catalog import UdfCacheCatalogEntry
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.create_statement import ColConstraintInfo, ColumnDefinition
from eva.utils.generic_utils import generate_file_path


def is_video_table(table: TableCatalogEntry):
    return table.table_type == TableType.VIDEO_DATA


def get_video_table_column_definitions() -> List[ColumnDefinition]:
    """
    name: video path
    id: frame id
    data: frame data
    """
    columns = [
        ColumnDefinition(
            "name", ColumnType.TEXT, None, None, ColConstraintInfo(unique=True)
        ),
        ColumnDefinition("id", ColumnType.INTEGER, None, None),
        ColumnDefinition(
            "data", ColumnType.NDARRAY, NdArrayType.UINT8, (None, None, None)
        ),
    ]
    return columns


def get_table_primary_columns(table_catalog_obj: TableCatalogEntry):
    if table_catalog_obj.table_type == TableType.VIDEO_DATA:
        return get_video_table_column_definitions()[:2]
    elif table_catalog_obj.table_type == TableType.IMAGE_DATA:
        return get_image_table_column_definitions()[:1]
    else:
        raise Exception(f"Unexpected table type {table_catalog_obj.table_type}")


def get_image_table_column_definitions() -> List[ColumnDefinition]:
    """
    name: image path
    data: image decoded data
    """
    columns = [
        ColumnDefinition(
            "name", ColumnType.TEXT, None, None, ColConstraintInfo(unique=True)
        ),
        ColumnDefinition(
            "data", ColumnType.NDARRAY, NdArrayType.UINT8, (None, None, None)
        ),
    ]
    return columns


def get_image_table_primary_columns():
    return get_image_table_column_definitions()[:1]


def xform_column_definitions_to_catalog_entries(
    col_list: List[ColumnDefinition],
) -> List[ColumnCatalogEntry]:
    """Create column catalog entries for the input parsed column list.

    Arguments:
        col_list {List[ColumnDefinition]} -- parsed col list to be created
    """
    if isinstance(col_list, ColumnDefinition):
        col_list = [col_list]

    result_list = []
    for col in col_list:
        column_entry = ColumnCatalogEntry(
            name=col.name,
            type=col.type,
            array_type=col.array_type,
            array_dimensions=col.dimension,
            is_nullable=col.cci.nullable,
        )
        # todo: change me
        result_list.append(column_entry)

    return result_list


def construct_udf_cache_catalog_entry(
    func_expr: FunctionExpression,
) -> UdfCacheCatalogEntry:
    """Constructs a udf cache catalog entry from a given function expression.

    It is assumed that the function expression has already been bound using the binder.
    The catalog entry is populated with dependent udfs and columns by traversing the
    expression tree. The cache name is represented by the signature of the function
    expression.

    Args:
        func_expr (FunctionExpression): the function expression with which the cache is
        assoicated

    Returns:
        UdfCacheCatalogEntry: the udf cache catalog entry
    """
    udf_depends = []
    col_depends = []
    for expr in func_expr.find_all(FunctionExpression):
        udf_depends.append(expr.udf_obj)
    for expr in func_expr.find_all(TupleValueExpression):
        col_depends.append(expr.col_obj)
    cache_name = func_expr.signature()
    cache_path = str(generate_file_path(cache_name))
    entry = UdfCacheCatalogEntry(
        name=func_expr.signature(),
        udf_id=func_expr.udf_obj.row_id,
        cache_path=cache_path,
        udf_depends=udf_depends,
        col_depends=col_depends,
    )

    return entry

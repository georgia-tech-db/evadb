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
from eva.parser.create_statement import ColConstraintInfo, ColumnDefinition


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
        ColumnDefinition("seconds", ColumnType.FLOAT, None, []),
    ]
    return columns


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

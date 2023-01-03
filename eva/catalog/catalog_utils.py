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
from eva.catalog.models.table_catalog import TableCatalog
from eva.parser.create_statement import ColConstraintInfo, ColumnDefinition


def is_video_table(table: TableCatalog):
    return table.table_type == TableType.VIDEO_DATA


def get_video_table_column_definitions() -> List[ColumnDefinition]:
    """
    name: video path
    id: frame id
    data: frame data
    """
    columns = [
        ColumnDefinition(
            "name", ColumnType.TEXT, None, [], ColConstraintInfo(unique=True)
        ),
        ColumnDefinition("id", ColumnType.INTEGER, None, []),
        ColumnDefinition(
            "data", ColumnType.NDARRAY, NdArrayType.UINT8, [None, None, None]
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
            "name", ColumnType.TEXT, None, [], ColConstraintInfo(unique=True)
        ),
        ColumnDefinition(
            "data", ColumnType.NDARRAY, NdArrayType.UINT8, [None, None, None]
        ),
    ]
    return columns

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

from src.parser.types import ParserColumnDataType
from src.catalog.column_type import ColumnType


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
        
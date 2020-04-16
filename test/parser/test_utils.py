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

import unittest
from src.parser.types import ParserColumnDataType
from src.catalog.column_type import ColumnType
from src.parser.utils import xform_parser_column_type_to_catalog_type


class ParserTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_xform_parser_column_type_to_catalog_type(self):
        col_type = ParserColumnDataType.BOOLEAN
        self.assertEqual(
            xform_parser_column_type_to_catalog_type(col_type),
            ColumnType.BOOLEAN)
        col_type = ParserColumnDataType.FLOAT
        self.assertEqual(
            xform_parser_column_type_to_catalog_type(col_type),
            ColumnType.FLOAT)
        col_type = ParserColumnDataType.INTEGER
        self.assertEqual(
            xform_parser_column_type_to_catalog_type(col_type),
            ColumnType.INTEGER)
        col_type = ParserColumnDataType.TEXT
        self.assertEqual(
            xform_parser_column_type_to_catalog_type(col_type),
            ColumnType.TEXT)
        col_type = ParserColumnDataType.NDARRAY
        self.assertEqual(
            xform_parser_column_type_to_catalog_type(col_type),
            ColumnType.NDARRAY)
  
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

from mock import patch, MagicMock

from src.expression.tuple_value_expression import TupleValueExpression
from src.optimizer.optimizer_utils import (bind_dataset, bind_tuple_value_expr,
                                           column_definition_to_udf_io)
from src.optimizer.optimizer_utils import \
    xform_parser_column_type_to_catalog_type
from src.parser.create_statement import ColumnDefinition
from src.parser.types import ParserColumnDataType
from src.catalog.column_type import ColumnType


class OptimizerUtilsTest(unittest.TestCase):

    @patch('src.optimizer.optimizer_utils.CatalogManager')
    def test_bind_dataset(self, mock):
        video = MagicMock()
        catalog = mock.return_value
        actual = bind_dataset(video)
        catalog.get_dataset_metadata.assert_called_with(video.database_name,
                                                        video.table_name)
        self.assertEqual(actual, catalog.get_dataset_metadata.return_value)

    def test_bind_tuple_value_expr(self):
        column_map = {'col1': object()}
        tuple_expr = TupleValueExpression(col_name="COL1")
        bind_tuple_value_expr(tuple_expr, column_map)
        self.assertEqual(tuple_expr.col_object, column_map['col1'])

    @patch('src.optimizer.optimizer_utils.CatalogManager')
    @patch('src.optimizer.optimizer_utils.\
xform_parser_column_type_to_catalog_type')
    def test_column_definition_to_udf_io(self, mock_func, mock):
        mock.return_value.udf_io.return_value = 'udf_io'
        col = MagicMock(spec=ColumnDefinition)
        col.name = 'name'
        col.type = 'type'
        col.dimension = 'dimension'
        col_list = [col, col]
        mock_func.return_value = col.type
        actual = column_definition_to_udf_io(col_list, True)
        for col in col_list:
            mock_func.assert_called_with('type')
            mock.return_value.udf_io.assert_called_with(
                'name', 'type', 'dimension', True)

        self.assertEqual(actual, ['udf_io', 'udf_io'])

        # input not list
        actual2 = column_definition_to_udf_io(col, True)
        mock.return_value.udf_io.assert_called_with(
            'name', 'type', 'dimension', True)
        self.assertEqual(actual2, ['udf_io'])

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

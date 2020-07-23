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

from mock import patch, MagicMock, call

from src.expression.function_expression import FunctionExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.optimizer.optimizer_utils import (bind_dataset, bind_tuple_value_expr,
                                           column_definition_to_udf_io,
                                           bind_function_expr,
                                           bind_predicate_expr,
                                           bind_columns_expr,
                                           create_video_metadata)
from src.parser.create_statement import ColumnDefinition
from src.parser.types import ParserColumnDataType


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
    @patch('src.optimizer.optimizer_utils.str_to_class')
    @unittest.skip("This testcase needs rework")
    def test_bind_function_value_expr(self, mock_str_path, mock_catalog):
        func_expr = FunctionExpression(None, name='temp')
        mock_output = MagicMock()
        mock_output.name = 'name'
        mock_output.impl_file_path = 'path'
        mock_catalog.return_value.get_udf_by_name.return_value = mock_output
        bind_function_expr(func_expr, None)

        mock_catalog.return_value.get_udf_by_name.assert_called_with('temp')
        mock_str_path.assert_called_with('path.name')
        self.assertEqual(func_expr.function,
                         mock_str_path.return_value.return_value)

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

    @patch('src.optimizer.optimizer_utils.bind_function_expr')
    def test_bind_predicate_calls_bind_func_expr_if_type_functional(self,
                                                                    mock_bind):
        func_expr = FunctionExpression(None, name='temp')
        bind_predicate_expr(func_expr, {})
        mock_bind.assert_called_with(func_expr, {})

    @patch('src.optimizer.optimizer_utils.bind_function_expr')
    def test_bind_columns_calls_bind_func_expr_if_type_functional(self,
                                                                  mock_bind):
        func_expr = FunctionExpression(None, name='temp')
        bind_columns_expr([func_expr], {})
        mock_bind.assert_called_with(func_expr, {})

    @patch('src.optimizer.optimizer_utils.CatalogManager')
    @patch('src.optimizer.optimizer_utils.ColumnDefinition')
    @patch('src.optimizer.optimizer_utils.ColumnConstraintInformation')
    @patch('src.optimizer.optimizer_utils.create_column_metadata')
    @patch('src.optimizer.optimizer_utils.generate_file_path')
    def test_create_video_metadata(self, m_gfp, m_ccm, m_cci, m_cd, m_cm):
        catalog_ins = MagicMock()
        expected = 'video_metadata'
        name = 'eva'
        uri = 'tmp'
        m_gfp.return_value = uri
        m_ccm.return_value = 'col_metadata'
        m_cci.return_value = 'cci'
        m_cd.return_value = 1
        m_cm.return_value = catalog_ins
        catalog_ins.create_metadata.return_value = expected

        calls = [call('id', ParserColumnDataType.INTEGER, [],
                      'cci'),
                 call('data', ParserColumnDataType.NDARRAY,
                      [None, None, None])]

        actual = create_video_metadata(name)
        m_gfp.assert_called_once_with(name)
        m_ccm.assert_called_once_with([1, 1])
        m_cci.assert_called_once_with(unique=True)
        m_cd.assert_has_calls(calls)
        catalog_ins.create_metadata.assert_called_with(
            name, uri, 'col_metadata', identifier_column='id')
        self.assertEqual(actual, expected)

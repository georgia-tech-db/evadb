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

from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.optimizer.optimizer_utils import (bind_dataset, bind_tuple_value_expr,
                                           column_definition_to_udf_io,
                                           bind_function_expr,
                                           bind_predicate_expr,
                                           bind_columns_expr,
                                           create_video_metadata,
                                           handle_if_not_exists)
from eva.parser.create_statement import ColumnDefinition
from eva.catalog.column_type import ColumnType, NdArrayType


class OptimizerUtilsTest(unittest.TestCase):

    @patch('eva.optimizer.optimizer_utils.CatalogManager')
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

    @patch('eva.optimizer.optimizer_utils.CatalogManager')
    @patch('eva.optimizer.optimizer_utils.path_to_class')
    def test_bind_function_value_expr(self, mock_str_path, mock_catalog):
        func_expr = FunctionExpression(None, name='temp')
        mock_output = MagicMock()
        mock_output.name = 'name'
        mock_output.impl_file_path = 'path'
        mock_catalog.return_value.get_udf_by_name.return_value = mock_output
        bind_function_expr(func_expr, None)

        mock_catalog.return_value.get_udf_by_name.assert_called_with('temp')
        mock_str_path.assert_called_with('path', 'name')
        self.assertEqual(func_expr.function,
                         mock_str_path.return_value.return_value)

    def test_column_definition_to_udf_io(self):
        col = ColumnDefinition('data', ColumnType.NDARRAY, NdArrayType.UINT8,
                               [None, None, None])
        col_list = [col, col]
        actual = column_definition_to_udf_io(col_list, True)
        for io in actual:
            self.assertEqual(io.name, 'data')
            self.assertEqual(io.type, ColumnType.NDARRAY)
            self.assertEqual(io.is_nullable, False)
            self.assertEqual(io.array_type, NdArrayType.UINT8)
            self.assertEqual(io.array_dimensions, [None, None, None])
            self.assertEqual(io.is_input, True)
            self.assertEqual(io.udf_id, None)

        # input not list
        actual2 = column_definition_to_udf_io(col, True)
        for io in actual2:
            self.assertEqual(io.name, 'data')
            self.assertEqual(io.type, ColumnType.NDARRAY)
            self.assertEqual(io.is_nullable, False)
            self.assertEqual(io.array_type, NdArrayType.UINT8)
            self.assertEqual(io.array_dimensions, [None, None, None])
            self.assertEqual(io.is_input, True)
            self.assertEqual(io.udf_id, None)

    @patch('eva.optimizer.optimizer_utils.bind_function_expr')
    def test_bind_predicate_calls_bind_func_expr_if_type_functional(self,
                                                                    mock_bind):
        func_expr = FunctionExpression(None, name='temp')
        bind_predicate_expr(func_expr, {})
        mock_bind.assert_called_with(func_expr, {})

    @patch('eva.optimizer.optimizer_utils.bind_function_expr')
    def test_bind_columns_calls_bind_func_expr_if_type_functional(self,
                                                                  mock_bind):
        func_expr = FunctionExpression(None, name='temp')
        bind_columns_expr([func_expr], {})
        mock_bind.assert_called_with(func_expr, {})

    @patch('eva.optimizer.optimizer_utils.CatalogManager')
    @patch('eva.optimizer.optimizer_utils.ColumnDefinition')
    @patch('eva.optimizer.optimizer_utils.ColConstraintInfo')
    @patch('eva.optimizer.optimizer_utils.create_column_metadata')
    @patch('eva.optimizer.optimizer_utils.generate_file_path')
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

        calls = [call('id', ColumnType.INTEGER, None, [],
                      'cci'),
                 call('data', ColumnType.NDARRAY, NdArrayType.UINT8,
                      [None, None, None])]

        actual = create_video_metadata(name)
        m_gfp.assert_called_once_with(name)
        m_ccm.assert_called_once_with([1, 1])
        m_cci.assert_called_once_with(unique=True)
        m_cd.assert_has_calls(calls)
        catalog_ins.create_metadata.assert_called_with(
            name, uri, 'col_metadata', identifier_column='id')
        self.assertEqual(actual, expected)

    @patch('eva.optimizer.optimizer_utils.CatalogManager.check_table_exists')
    def test_handle_if_not_exists_raises_error(self, check_mock):
        check_mock.return_value = True
        with self.assertRaises(RuntimeError):
            handle_if_not_exists(check_mock, False)

    @patch('eva.optimizer.optimizer_utils.CatalogManager.check_table_exists')
    def test_handle_if_not_exists_return_True(self, check_mock):
        check_mock.return_value = True
        self.assertTrue(handle_if_not_exists(check_mock, True))

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
import numpy as np
from petastorm.codecs import NdarrayCodec
from petastorm.codecs import ScalarCodec
from petastorm.unischema import UnischemaField
from pyspark.sql.types import IntegerType, FloatType, StringType

from decimal import Decimal
from unittest.mock import MagicMock, call, patch
from src.catalog.column_type import ColumnType, NdArrayType
from src.catalog.df_schema import DataFrameSchema
from src.catalog.models.df_column import DataFrameColumn
from src.catalog.schema_utils import SchemaUtils


class SchemaTests(unittest.TestCase):

    # TEST SCHEMA UTILS START

    def test_get_petastorm_column(self):
        col_name = 'frame_id'
        col = DataFrameColumn(col_name, ColumnType.INTEGER, False)
        petastorm_col = UnischemaField(
            col_name, np.int32, (), ScalarCodec(
                IntegerType()), False)
        self.assertEqual(SchemaUtils.get_petastorm_column(col), petastorm_col)

        col = DataFrameColumn(col_name, ColumnType.FLOAT, True)
        petastorm_col = UnischemaField(
            col_name, np.float64, (), ScalarCodec(
                FloatType()), True)
        self.assertEqual(SchemaUtils.get_petastorm_column(col), petastorm_col)

        col = DataFrameColumn(col_name, ColumnType.TEXT, False)
        petastorm_col = UnischemaField(
            col_name, np.str_, (), ScalarCodec(
                StringType()), False)
        self.assertEqual(SchemaUtils.get_petastorm_column(col), petastorm_col)

        col = DataFrameColumn(col_name, None, True, [10, 10])
        self.assertEqual(SchemaUtils.get_petastorm_column(col), None)

    def test_get_petastorm_column_ndarray(self):
        expected_type = [np.int8, np.uint8, np.int16, np.int32, np.int64,
                         np.unicode_, np.bool_, np.float32, np.float64,
                         Decimal, np.str_, np.datetime64]
        col_name = 'frame_id'
        for array_type, np_type in zip(NdArrayType, expected_type):
            col = DataFrameColumn(col_name, ColumnType.NDARRAY, True,
                                  array_type, [10, 10])
            petastorm_col = UnischemaField(col_name, np_type, [10, 10],
                                           NdarrayCodec(), True)
            self.assertEqual(SchemaUtils.get_petastorm_column(col),
                             petastorm_col)

    def test_raise_exception_when_unkown_array_type(self):
        col_name = 'frame_id'
        col = DataFrameColumn(col_name, ColumnType.NDARRAY, True,
                              ColumnType.TEXT, [10, 10])
        self.assertRaises(ValueError, SchemaUtils.get_petastorm_column, col)

    @patch('src.catalog.schema_utils.Unischema')
    @patch('src.catalog.schema_utils.SchemaUtils.get_petastorm_column')
    def test_get_petastorm_schema(self, mock_get_pc, mock_uni):
        cols = [MagicMock() for i in range(2)]
        mock_get_pc.side_effect = [1, 2]
        self.assertEqual(
            SchemaUtils.get_petastorm_schema(
                'name', cols), mock_uni.return_value)
        mock_get_pc.assert_has_calls([call(cols[0]), call(cols[1])])
        mock_uni.assert_called_once_with('name', [1, 2])

    # TEST SCHEMA UTILS END

    # TEST DF_SCHEMA START
    def test_df_schema(self):
        schema_name = "foo"
        column_1 = DataFrameColumn("frame_id", ColumnType.INTEGER, False)
        column_2 = DataFrameColumn("frame_data", ColumnType.NDARRAY, False,
                                   NdArrayType.UINT8, [28, 28])
        column_3 = DataFrameColumn("frame_label", ColumnType.INTEGER, False)
        col_list = [column_1, column_2, column_3]
        schema = DataFrameSchema(schema_name, col_list)
        expected_schema = SchemaUtils.get_petastorm_schema(
            schema_name, col_list)
        self.assertEqual(schema.name, schema_name)
        self.assertEqual(schema.column_list, col_list)
        self.assertEqual(
            schema.petastorm_schema.fields,
            expected_schema.fields)
        for field1, field2 in zip(
                schema.petastorm_schema.fields, expected_schema.fields):
            self.assertEqual(field1, field2)
        self.assertEqual(
            schema.pyspark_schema,
            expected_schema.as_spark_schema())

    def test_schema_equality(self):
        schema_name = "foo"
        column_1 = DataFrameColumn("frame_id", ColumnType.INTEGER, False)
        column_2 = DataFrameColumn("frame_data", ColumnType.NDARRAY, False,
                                   NdArrayType.UINT8, [28, 28])
        column_3 = DataFrameColumn("frame_label", ColumnType.INTEGER, False)
        col_list = [column_1, column_2, column_3]
        schema1 = DataFrameSchema(schema_name, col_list)
        schema2 = DataFrameSchema(schema_name, col_list[1:])
        schema3 = DataFrameColumn('foo2', col_list)
        self.assertEqual(schema1, schema1)
        self.assertNotEqual(schema1, schema2)
        self.assertNotEqual(schema1, schema3)

    # TEST DF_SCHEMA END

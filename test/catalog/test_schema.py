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
import unittest

from eva.catalog.column_type import ColumnType, NdArrayType
from eva.catalog.df_schema import DataFrameSchema
from eva.catalog.models.df_column import DataFrameColumn


class SchemaTests(unittest.TestCase):

    # TEST SCHEMA UTILS START

    def test_schema_equality(self):
        schema_name = "foo"
        column_1 = DataFrameColumn("frame_id", ColumnType.INTEGER, False)
        column_2 = DataFrameColumn(
            "frame_data", ColumnType.NDARRAY, False, NdArrayType.UINT8, [28, 28]
        )
        column_3 = DataFrameColumn("frame_label", ColumnType.INTEGER, False)
        col_list = [column_1, column_2, column_3]
        schema1 = DataFrameSchema(schema_name, col_list)
        schema2 = DataFrameSchema(schema_name, col_list[1:])
        schema3 = DataFrameColumn("foo2", col_list)
        self.assertEqual(schema1, schema1)
        self.assertNotEqual(schema1, schema2)
        self.assertNotEqual(schema1, schema3)

    # TEST DF_SCHEMA END

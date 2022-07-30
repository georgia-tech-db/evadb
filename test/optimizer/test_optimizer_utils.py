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
from eva.optimizer.optimizer_utils import column_definition_to_udf_io
from eva.parser.create_statement import ColumnDefinition


class OptimizerUtilsTest(unittest.TestCase):
    def test_column_definition_to_udf_io(self):
        col = ColumnDefinition(
            "data", ColumnType.NDARRAY, NdArrayType.UINT8, [None, None, None]
        )
        col_list = [col, col]
        actual = column_definition_to_udf_io(col_list, True)
        for io in actual:
            self.assertEqual(io.name, "data")
            self.assertEqual(io.type, ColumnType.NDARRAY)
            self.assertEqual(io.is_nullable, False)
            self.assertEqual(io.array_type, NdArrayType.UINT8)
            self.assertEqual(io.array_dimensions, [None, None, None])
            self.assertEqual(io.is_input, True)
            self.assertEqual(io.udf_id, None)

        # input not list
        actual2 = column_definition_to_udf_io(col, True)
        for io in actual2:
            self.assertEqual(io.name, "data")
            self.assertEqual(io.type, ColumnType.NDARRAY)
            self.assertEqual(io.is_nullable, False)
            self.assertEqual(io.array_type, NdArrayType.UINT8)
            self.assertEqual(io.array_dimensions, [None, None, None])
            self.assertEqual(io.is_input, True)
            self.assertEqual(io.udf_id, None)

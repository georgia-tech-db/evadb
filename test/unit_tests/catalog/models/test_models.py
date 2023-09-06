# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from evadb.catalog.catalog_type import ColumnType, NdArrayType, TableType
from evadb.catalog.models.column_catalog import ColumnCatalogEntry
from evadb.catalog.models.function_catalog import FunctionCatalogEntry
from evadb.catalog.models.function_io_catalog import FunctionIOCatalogEntry
from evadb.catalog.models.index_catalog import IndexCatalogEntry
from evadb.catalog.models.table_catalog import TableCatalogEntry


class CatalogModelsTest(unittest.TestCase):
    def test_df_column(self):
        df_col = ColumnCatalogEntry("name", ColumnType.TEXT, is_nullable=False)
        df_col.array_dimensions = [1, 2]
        df_col.table_id = 1
        self.assertEqual(df_col.array_type, None)
        self.assertEqual(df_col.array_dimensions, [1, 2])
        self.assertEqual(df_col.is_nullable, False)
        self.assertEqual(df_col.name, "name")
        self.assertEqual(df_col.type, ColumnType.TEXT)
        self.assertEqual(df_col.table_id, 1)
        self.assertEqual(df_col.row_id, None)

    def test_df_equality(self):
        df_col = ColumnCatalogEntry("name", ColumnType.TEXT, is_nullable=False)
        self.assertEqual(df_col, df_col)
        df_col1 = ColumnCatalogEntry("name2", ColumnType.TEXT, is_nullable=False)
        self.assertNotEqual(df_col, df_col1)
        df_col1 = ColumnCatalogEntry("name", ColumnType.INTEGER, is_nullable=False)
        self.assertNotEqual(df_col, df_col1)
        df_col1 = ColumnCatalogEntry("name", ColumnType.INTEGER, is_nullable=True)
        self.assertNotEqual(df_col, df_col1)
        df_col1 = ColumnCatalogEntry("name", ColumnType.INTEGER, is_nullable=False)
        self.assertNotEqual(df_col, df_col1)
        df_col._array_dimensions = [2, 4]
        df_col1 = ColumnCatalogEntry(
            "name", ColumnType.INTEGER, is_nullable=False, array_dimensions=[1, 2]
        )
        self.assertNotEqual(df_col, df_col1)

        df_col._table_id = 1
        df_col1 = ColumnCatalogEntry(
            "name",
            ColumnType.INTEGER,
            is_nullable=False,
            array_dimensions=[2, 4],
            table_id=2,
        )
        self.assertNotEqual(df_col, df_col1)

    def test_table_catalog_entry_equality(self):
        column_1 = ColumnCatalogEntry("frame_id", ColumnType.INTEGER, False)
        column_2 = ColumnCatalogEntry("frame_label", ColumnType.INTEGER, False)
        col_list = [column_1, column_2]
        table_catalog_entry = TableCatalogEntry(
            "name", "evadb_dataset", table_type=TableType.VIDEO_DATA, columns=col_list
        )
        self.assertEqual(table_catalog_entry, table_catalog_entry)

        table_catalog_entry1 = TableCatalogEntry(
            "name2", "evadb_dataset", table_type=TableType.VIDEO_DATA, columns=col_list
        )

        self.assertNotEqual(table_catalog_entry, table_catalog_entry1)

    def test_function(self):
        function = FunctionCatalogEntry(
            "function", "fasterRCNN", "ObjectDetection", "checksum"
        )
        self.assertEqual(function.row_id, None)
        self.assertEqual(function.impl_file_path, "fasterRCNN")
        self.assertEqual(function.name, "function")
        self.assertEqual(function.type, "ObjectDetection")
        self.assertEqual(function.checksum, "checksum")

    def test_function_hash(self):
        function1 = FunctionCatalogEntry(
            "function", "fasterRCNN", "ObjectDetection", "checksum"
        )
        function2 = FunctionCatalogEntry(
            "function", "fasterRCNN", "ObjectDetection", "checksum"
        )

        self.assertEqual(hash(function1), hash(function2))

    def test_function_equality(self):
        function = FunctionCatalogEntry(
            "function", "fasterRCNN", "ObjectDetection", "checksum"
        )
        self.assertEqual(function, function)
        function2 = FunctionCatalogEntry(
            "function2", "fasterRCNN", "ObjectDetection", "checksum"
        )
        self.assertNotEqual(function, function2)
        function3 = FunctionCatalogEntry(
            "function", "fasterRCNN2", "ObjectDetection", "checksum"
        )
        self.assertNotEqual(function, function3)
        function4 = FunctionCatalogEntry(
            "function2", "fasterRCNN", "ObjectDetection3", "checksum"
        )
        self.assertNotEqual(function, function4)

    def test_function_io(self):
        function_io = FunctionIOCatalogEntry(
            "name", ColumnType.NDARRAY, True, NdArrayType.UINT8, [2, 3], True, 1
        )
        self.assertEqual(function_io.row_id, None)
        self.assertEqual(function_io.function_id, 1)
        self.assertEqual(function_io.is_input, True)
        self.assertEqual(function_io.is_nullable, True)
        self.assertEqual(function_io.array_type, NdArrayType.UINT8)
        self.assertEqual(function_io.array_dimensions, [2, 3])
        self.assertEqual(function_io.name, "name")
        self.assertEqual(function_io.type, ColumnType.NDARRAY)

    def test_function_io_equality(self):
        function_io = FunctionIOCatalogEntry(
            "name", ColumnType.FLOAT, True, None, [2, 3], True, 1
        )
        self.assertEqual(function_io, function_io)
        function_io2 = FunctionIOCatalogEntry(
            "name2", ColumnType.FLOAT, True, None, [2, 3], True, 1
        )
        self.assertNotEqual(function_io, function_io2)
        function_io2 = FunctionIOCatalogEntry(
            "name", ColumnType.INTEGER, True, None, [2, 3], True, 1
        )
        self.assertNotEqual(function_io, function_io2)
        function_io2 = FunctionIOCatalogEntry(
            "name", ColumnType.FLOAT, False, None, [2, 3], True, 1
        )
        self.assertNotEqual(function_io, function_io2)
        function_io2 = FunctionIOCatalogEntry(
            "name", ColumnType.FLOAT, True, None, [2, 3, 4], True, 1
        )
        self.assertNotEqual(function_io, function_io2)
        function_io2 = FunctionIOCatalogEntry(
            "name", ColumnType.FLOAT, True, None, [2, 3], False, 1
        )
        self.assertNotEqual(function_io, function_io2)
        function_io2 = FunctionIOCatalogEntry(
            "name", ColumnType.FLOAT, True, None, [2, 3], True, 2
        )
        self.assertNotEqual(function_io, function_io2)

    def test_index(self):
        index = IndexCatalogEntry("index", "FaissSavePath", "HNSW")
        self.assertEqual(index.row_id, None)
        self.assertEqual(index.name, "index")
        self.assertEqual(index.save_file_path, "FaissSavePath")
        self.assertEqual(index.type, "HNSW")

    def test_index_hash(self):
        index1 = IndexCatalogEntry("index", "FaissSavePath", "HNSW")
        index2 = IndexCatalogEntry("index", "FaissSavePath", "HNSW")

        self.assertEqual(hash(index1), hash(index2))

    def test_index_equality(self):
        index = IndexCatalogEntry("index", "FaissSavePath", "HNSW")
        self.assertEqual(index, index)
        index2 = IndexCatalogEntry("index2", "FaissSavePath", "HNSW")
        self.assertNotEqual(index, index2)
        index3 = IndexCatalogEntry("index", "FaissSavePath3", "HNSW")
        self.assertNotEqual(index, index3)
        index4 = IndexCatalogEntry("index", "FaissSavePath", "HNSW4")
        self.assertNotEqual(index, index4)

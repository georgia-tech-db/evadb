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

from eva.catalog.catalog_type import ColumnType, NdArrayType, TableType
from eva.catalog.df_schema import DataFrameSchema
from eva.catalog.models.column_catalog import ColumnCatalog
from eva.catalog.models.index_catalog import IndexCatalog
from eva.catalog.models.table_catalog import TableCatalog
from eva.catalog.models.udf_catalog import UdfCatalog
from eva.catalog.models.udf_io_catalog import UdfIOCatalog


class CatalogModelsTest(unittest.TestCase):
    def test_df_column(self):
        df_col = ColumnCatalog("name", ColumnType.TEXT, is_nullable=False)
        df_col.array_dimensions = [1, 2]
        df_col.table_id = 1
        self.assertEqual(df_col.array_type, None)
        self.assertEqual(df_col.array_dimensions, [1, 2])
        self.assertEqual(df_col.is_nullable, False)
        self.assertEqual(df_col.name, "name")
        self.assertEqual(df_col.type, ColumnType.TEXT)
        self.assertEqual(df_col.table_id, 1)
        self.assertEqual(df_col.row_id, None)
        self.assertEqual(str(df_col), "Column: (name, TEXT, False, None[1, 2])")

    def test_df_equality(self):
        df_col = ColumnCatalog("name", ColumnType.TEXT, is_nullable=False)
        self.assertEqual(df_col, df_col)
        df_col1 = ColumnCatalog("name2", ColumnType.TEXT, is_nullable=False)
        self.assertNotEqual(df_col, df_col1)
        df_col1 = ColumnCatalog("name", ColumnType.INTEGER, is_nullable=False)
        self.assertNotEqual(df_col, df_col1)
        df_col1 = ColumnCatalog("name", ColumnType.INTEGER, is_nullable=True)
        self.assertNotEqual(df_col, df_col1)
        df_col1 = ColumnCatalog("name", ColumnType.INTEGER, is_nullable=False)
        self.assertNotEqual(df_col, df_col1)
        df_col.array_dimensions = [2, 4]
        df_col1 = ColumnCatalog(
            "name", ColumnType.INTEGER, is_nullable=False, array_dimensions=[1, 2]
        )
        self.assertNotEqual(df_col, df_col1)

        df_col.table_id = 1
        df_col1 = ColumnCatalog(
            "name",
            ColumnType.INTEGER,
            is_nullable=False,
            array_dimensions=[2, 4],
            table_id=2,
        )
        self.assertNotEqual(df_col, df_col1)

    def test_table_catalog_entry(self):
        table_catalog_entry = TableCatalog(
            "name", "eva_dataset", table_type=TableType.VIDEO_DATA
        )
        column_1 = ColumnCatalog("frame_id", ColumnType.INTEGER, False)
        column_2 = ColumnCatalog("frame_label", ColumnType.INTEGER, False)
        col_list = [column_1, column_2]
        schema = DataFrameSchema("name", col_list)
        table_catalog_entry.schema = col_list

        self.assertEqual(table_catalog_entry.name, "name")
        self.assertEqual(table_catalog_entry.file_url, "eva_dataset")
        self.assertEqual(table_catalog_entry.row_id, None)
        self.assertEqual(table_catalog_entry.identifier_column, "id")
        self.assertEqual(table_catalog_entry.schema, schema)
        self.assertEqual(table_catalog_entry.table_type, TableType.VIDEO_DATA)

    def test_table_catalog_entry_equality(self):
        table_catalog_entry = TableCatalog(
            "name", "eva_dataset", table_type=TableType.VIDEO_DATA
        )
        column_1 = ColumnCatalog("frame_id", ColumnType.INTEGER, False)
        column_2 = ColumnCatalog("frame_label", ColumnType.INTEGER, False)
        col_list = [column_1, column_2]
        table_catalog_entry.schema = col_list
        self.assertEqual(table_catalog_entry, table_catalog_entry)

        table_catalog_entry1 = TableCatalog(
            "name2", "eva_dataset", table_type=TableType.VIDEO_DATA
        )
        column_1 = ColumnCatalog("frame_id", ColumnType.INTEGER, False)
        column_2 = ColumnCatalog("frame_label", ColumnType.INTEGER, False)
        col_list = [column_1, column_2]
        table_catalog_entry1.schema = col_list
        self.assertNotEqual(table_catalog_entry, table_catalog_entry1)
        table_catalog_entry2 = TableCatalog(
            "name2", "eva_dataset", table_type=TableType.VIDEO_DATA
        )
        table_catalog_entry2.schema = col_list[1:]
        self.assertNotEqual(table_catalog_entry1, table_catalog_entry2)

    def test_udf(self):
        udf = UdfCatalog("udf", "fasterRCNN", "ObjectDetection")
        self.assertEqual(udf.row_id, None)
        self.assertEqual(udf.impl_file_path, "fasterRCNN")
        self.assertEqual(udf.name, "udf")
        self.assertEqual(udf.type, "ObjectDetection")
        self.assertEqual(str(udf), "udf: (udf, fasterRCNN, ObjectDetection)\n")

    def test_udf_hash(self):
        udf1 = UdfCatalog("udf", "fasterRCNN", "ObjectDetection")
        udf2 = UdfCatalog("udf", "fasterRCNN", "ObjectDetection")

        self.assertEqual(hash(udf1), hash(udf2))

    def test_udf_equality(self):
        udf = UdfCatalog("udf", "fasterRCNN", "ObjectDetection")
        self.assertEqual(udf, udf)
        udf2 = UdfCatalog("udf2", "fasterRCNN", "ObjectDetection")
        self.assertNotEqual(udf, udf2)
        udf3 = UdfCatalog("udf", "fasterRCNN2", "ObjectDetection")
        self.assertNotEqual(udf, udf3)
        udf4 = UdfCatalog("udf2", "fasterRCNN", "ObjectDetection3")
        self.assertNotEqual(udf, udf4)

    def test_udf_io(self):
        udf_io = UdfIOCatalog(
            "name", ColumnType.NDARRAY, True, NdArrayType.UINT8, [2, 3], True, 1
        )
        self.assertEqual(udf_io.row_id, None)
        self.assertEqual(udf_io.udf_id, 1)
        self.assertEqual(udf_io.is_input, True)
        self.assertEqual(udf_io.is_nullable, True)
        self.assertEqual(udf_io.array_type, NdArrayType.UINT8)
        self.assertEqual(udf_io.array_dimensions, [2, 3])
        self.assertEqual(udf_io.name, "name")
        self.assertEqual(udf_io.type, ColumnType.NDARRAY)

    def test_udf_io_equality(self):
        udf_io = UdfIOCatalog("name", ColumnType.FLOAT, True, None, [2, 3], True, 1)
        self.assertEqual(udf_io, udf_io)
        udf_io2 = UdfIOCatalog("name2", ColumnType.FLOAT, True, None, [2, 3], True, 1)
        self.assertNotEqual(udf_io, udf_io2)
        udf_io2 = UdfIOCatalog("name", ColumnType.INTEGER, True, None, [2, 3], True, 1)
        self.assertNotEqual(udf_io, udf_io2)
        udf_io2 = UdfIOCatalog("name", ColumnType.FLOAT, False, None, [2, 3], True, 1)
        self.assertNotEqual(udf_io, udf_io2)
        udf_io2 = UdfIOCatalog("name", ColumnType.FLOAT, True, None, [2, 3, 4], True, 1)
        self.assertNotEqual(udf_io, udf_io2)
        udf_io2 = UdfIOCatalog("name", ColumnType.FLOAT, True, None, [2, 3], False, 1)
        self.assertNotEqual(udf_io, udf_io2)
        udf_io2 = UdfIOCatalog("name", ColumnType.FLOAT, True, None, [2, 3], True, 2)
        self.assertNotEqual(udf_io, udf_io2)

    def test_index(self):
        index = IndexCatalog("index", "FaissSavePath", "HNSW")
        self.assertEqual(index.row_id, None)
        self.assertEqual(index.name, "index")
        self.assertEqual(index.save_file_path, "FaissSavePath")
        self.assertEqual(index.type, "HNSW")
        self.assertEqual(str(index), "index: (index, FaissSavePath, HNSW)\n")

    def test_index_hash(self):
        index1 = IndexCatalog("index", "FaissSavePath", "HNSW")
        index2 = IndexCatalog("index", "FaissSavePath", "HNSW")

        self.assertEqual(hash(index1), hash(index2))

    def test_index_equality(self):
        index = IndexCatalog("index", "FaissSavePath", "HNSW")
        self.assertEqual(index, index)
        index2 = IndexCatalog("index2", "FaissSavePath", "HNSW")
        self.assertNotEqual(index, index2)
        index3 = IndexCatalog("index", "FaissSavePath3", "HNSW")
        self.assertNotEqual(index, index3)
        index4 = IndexCatalog("index", "FaissSavePath", "HNSW4")
        self.assertNotEqual(index, index4)

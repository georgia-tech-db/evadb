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
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.catalog.models.udf import UdfMetadata
from eva.catalog.models.udf_io import UdfIO


class CatalogModelsTest(unittest.TestCase):
    def test_df_column(self):
        df_col = DataFrameColumn("name", ColumnType.TEXT, is_nullable=False)
        df_col.array_dimensions = [1, 2]
        df_col.metadata_id = 1
        self.assertEqual(df_col.array_type, None)
        self.assertEqual(df_col.array_dimensions, [1, 2])
        self.assertEqual(df_col.is_nullable, False)
        self.assertEqual(df_col.name, "name")
        self.assertEqual(df_col.type, ColumnType.TEXT)
        self.assertEqual(df_col.metadata_id, 1)
        self.assertEqual(df_col.id, None)
        self.assertEqual(str(df_col), "Column: (name, TEXT, False, None[1, 2])")

    def test_df_equality(self):
        df_col = DataFrameColumn("name", ColumnType.TEXT, is_nullable=False)
        self.assertEqual(df_col, df_col)
        df_col1 = DataFrameColumn("name2", ColumnType.TEXT, is_nullable=False)
        self.assertNotEqual(df_col, df_col1)
        df_col1 = DataFrameColumn("name", ColumnType.INTEGER, is_nullable=False)
        self.assertNotEqual(df_col, df_col1)
        df_col1 = DataFrameColumn("name", ColumnType.INTEGER, is_nullable=True)
        self.assertNotEqual(df_col, df_col1)
        df_col1 = DataFrameColumn("name", ColumnType.INTEGER, is_nullable=False)
        self.assertNotEqual(df_col, df_col1)
        df_col.array_dimensions = [2, 4]
        df_col1 = DataFrameColumn(
            "name", ColumnType.INTEGER, is_nullable=False, array_dimensions=[1, 2]
        )
        self.assertNotEqual(df_col, df_col1)

        df_col.metadata_id = 1
        df_col1 = DataFrameColumn(
            "name",
            ColumnType.INTEGER,
            is_nullable=False,
            array_dimensions=[2, 4],
            metadata_id=2,
        )
        self.assertNotEqual(df_col, df_col1)

    def test_df_metadata(self):
        df_metadata = DataFrameMetadata("name", "eva_dataset")
        column_1 = DataFrameColumn("frame_id", ColumnType.INTEGER, False)
        column_2 = DataFrameColumn("frame_label", ColumnType.INTEGER, False)
        col_list = [column_1, column_2]
        schema = DataFrameSchema("name", col_list)
        df_metadata.schema = col_list

        self.assertEqual(df_metadata.name, "name")
        self.assertEqual(df_metadata.file_url, "eva_dataset")
        self.assertEqual(df_metadata.id, None)
        self.assertEqual(df_metadata.identifier_column, "id")
        self.assertEqual(df_metadata.schema, schema)

    def test_df_metadata_equality(self):
        df_metadata = DataFrameMetadata("name", "eva_dataset")
        column_1 = DataFrameColumn("frame_id", ColumnType.INTEGER, False)
        column_2 = DataFrameColumn("frame_label", ColumnType.INTEGER, False)
        col_list = [column_1, column_2]
        df_metadata.schema = col_list
        self.assertEqual(df_metadata, df_metadata)

        df_metadata1 = DataFrameMetadata("name2", "eva_dataset")
        column_1 = DataFrameColumn("frame_id", ColumnType.INTEGER, False)
        column_2 = DataFrameColumn("frame_label", ColumnType.INTEGER, False)
        col_list = [column_1, column_2]
        df_metadata1.schema = col_list
        self.assertNotEqual(df_metadata, df_metadata1)
        df_metadata2 = DataFrameMetadata("name2", "eva_dataset")
        df_metadata2.schema = col_list[1:]
        self.assertNotEqual(df_metadata1, df_metadata2)

    def test_udf(self):
        udf = UdfMetadata("udf", "fasterRCNN", "ObjectDetection")
        self.assertEqual(udf.id, None)
        self.assertEqual(udf.impl_file_path, "fasterRCNN")
        self.assertEqual(udf.name, "udf")
        self.assertEqual(udf.type, "ObjectDetection")
        self.assertEqual(str(udf), "udf: (udf, fasterRCNN, ObjectDetection)\n")

    def test_udf_hash(self):
        udf1 = UdfMetadata("udf", "fasterRCNN", "ObjectDetection")
        udf2 = UdfMetadata("udf", "fasterRCNN", "ObjectDetection")

        self.assertEqual(hash(udf1), hash(udf2))

    def test_udf_equality(self):
        udf = UdfMetadata("udf", "fasterRCNN", "ObjectDetection")
        self.assertEqual(udf, udf)
        udf2 = UdfMetadata("udf2", "fasterRCNN", "ObjectDetection")
        self.assertNotEqual(udf, udf2)
        udf3 = UdfMetadata("udf", "fasterRCNN2", "ObjectDetection")
        self.assertNotEqual(udf, udf3)
        udf4 = UdfMetadata("udf2", "fasterRCNN", "ObjectDetection3")
        self.assertNotEqual(udf, udf4)

    def test_udf_io(self):
        udf_io = UdfIO(
            "name", ColumnType.NDARRAY, True, NdArrayType.UINT8, [2, 3], True, 1
        )
        self.assertEqual(udf_io.id, None)
        self.assertEqual(udf_io.udf_id, 1)
        self.assertEqual(udf_io.is_input, True)
        self.assertEqual(udf_io.is_nullable, True)
        self.assertEqual(udf_io.array_type, NdArrayType.UINT8)
        self.assertEqual(udf_io.array_dimensions, [2, 3])
        self.assertEqual(udf_io.name, "name")
        self.assertEqual(udf_io.type, ColumnType.NDARRAY)

    def test_udf_io_equality(self):
        udf_io = UdfIO("name", ColumnType.FLOAT, True, None, [2, 3], True, 1)
        self.assertEqual(udf_io, udf_io)
        udf_io2 = UdfIO("name2", ColumnType.FLOAT, True, None, [2, 3], True, 1)
        self.assertNotEqual(udf_io, udf_io2)
        udf_io2 = UdfIO("name", ColumnType.INTEGER, True, None, [2, 3], True, 1)
        self.assertNotEqual(udf_io, udf_io2)
        udf_io2 = UdfIO("name", ColumnType.FLOAT, False, None, [2, 3], True, 1)
        self.assertNotEqual(udf_io, udf_io2)
        udf_io2 = UdfIO("name", ColumnType.FLOAT, True, None, [2, 3, 4], True, 1)
        self.assertNotEqual(udf_io, udf_io2)
        udf_io2 = UdfIO("name", ColumnType.FLOAT, True, None, [2, 3], False, 1)
        self.assertNotEqual(udf_io, udf_io2)
        udf_io2 = UdfIO("name", ColumnType.FLOAT, True, None, [2, 3], True, 2)
        self.assertNotEqual(udf_io, udf_io2)

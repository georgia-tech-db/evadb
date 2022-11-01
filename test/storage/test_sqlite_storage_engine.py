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
import shutil
import unittest
from test.util import create_dummy_batches

from eva.catalog.column_type import ColumnType, NdArrayType
from eva.catalog.models.df_column import DataFrameColumn
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.storage.sqlite_storage_engine import SQLStorageEngine


class SQLStorageEngineTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = None

    def create_sample_table(self):
        table_info = DataFrameMetadata("dataset", "dataset")
        column_0 = DataFrameColumn("name", ColumnType.TEXT, False)
        column_1 = DataFrameColumn("id", ColumnType.INTEGER, False)
        column_2 = DataFrameColumn(
            "data", ColumnType.NDARRAY, False, NdArrayType.UINT8, [2, 2, 3]
        )
        table_info.schema = [column_0, column_1, column_2]
        return table_info

    def setUp(self):
        self.table = self.create_sample_table()

    def tearDown(self):
        try:
            shutil.rmtree("dataset", ignore_errors=True)
        except ValueError:
            pass

    def test_should_create_empty_table(self):
        sqlengine = SQLStorageEngine()
        sqlengine.create(self.table)
        records = list(sqlengine.read(self.table, batch_mem_size=3000))
        self.assertEqual(records, [])
        # clean up
        sqlengine.drop(self.table)

    def test_should_write_rows_to_table(self):
        dummy_batches = list(create_dummy_batches())

        sqlengine = SQLStorageEngine()
        sqlengine.create(self.table)
        for batch in dummy_batches:
            batch.drop_column_alias()
            sqlengine.write(self.table, batch)

        read_batch = list(sqlengine.read(self.table, batch_mem_size=3000))
        self.assertTrue(read_batch, dummy_batches)
        # clean up
        sqlengine.drop(self.table)

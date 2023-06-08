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
import shutil
import unittest
from test.util import (
    create_dummy_batches,
    get_evadb_for_testing,
    suffix_pytest_xdist_worker_id_to_dir,
)

import pytest

from evadb.catalog.catalog_type import ColumnType, NdArrayType, TableType
from evadb.catalog.models.column_catalog import ColumnCatalogEntry
from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.storage.sqlite_storage_engine import SQLStorageEngine


@pytest.mark.notparallel
class SQLStorageEngineTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = None

    def create_sample_table(self):
        table_info = TableCatalogEntry(
            str(suffix_pytest_xdist_worker_id_to_dir("dataset")),
            str(suffix_pytest_xdist_worker_id_to_dir("dataset")),
            table_type=TableType.VIDEO_DATA,
        )
        column_0 = ColumnCatalogEntry("name", ColumnType.TEXT, is_nullable=False)
        column_1 = ColumnCatalogEntry("id", ColumnType.INTEGER, is_nullable=False)
        column_2 = ColumnCatalogEntry(
            "data", ColumnType.NDARRAY, False, NdArrayType.UINT8, [2, 2, 3]
        )
        table_info.schema = [column_0, column_1, column_2]
        return table_info

    def setUp(self):
        self.table = self.create_sample_table()

    def tearDown(self):
        try:
            shutil.rmtree(
                suffix_pytest_xdist_worker_id_to_dir("dataset"), ignore_errors=True
            )
        except ValueError:
            pass

    def test_should_create_empty_table(self):
        evadb = get_evadb_for_testing()
        sqlengine = SQLStorageEngine(evadb)
        sqlengine.create(self.table)
        records = list(sqlengine.read(self.table, batch_mem_size=3000))
        self.assertEqual(len(records), 0)
        # clean up
        sqlengine.drop(self.table)

    def test_should_write_rows_to_table(self):
        dummy_batches = list(create_dummy_batches())
        # drop the _row_id
        dummy_batches = [batch.project(batch.columns[1:]) for batch in dummy_batches]
        evadb = get_evadb_for_testing()
        sqlengine = SQLStorageEngine(evadb)
        sqlengine.create(self.table)
        for batch in dummy_batches:
            batch.drop_column_alias()
            sqlengine.write(self.table, batch)

        read_batch = list(sqlengine.read(self.table, batch_mem_size=3000))
        self.assertTrue(read_batch, dummy_batches)
        # clean up
        sqlengine.drop(self.table)

    def test_rename(self):
        table_info = TableCatalogEntry(
            "new_name", "new_name", table_type=TableType.VIDEO_DATA
        )
        evadb = get_evadb_for_testing()
        sqlengine = SQLStorageEngine(evadb)

        with pytest.raises(Exception):
            sqlengine.rename(self.table, table_info)

    def test_sqlite_storage_engine_exceptions(self):
        evadb = get_evadb_for_testing()
        sqlengine = SQLStorageEngine(evadb)

        missing_table_info = TableCatalogEntry(
            "missing_table", None, table_type=TableType.VIDEO_DATA
        )

        with self.assertRaises(Exception):
            sqlengine.drop(missing_table_info)

        with self.assertRaises(Exception):
            sqlengine.write(missing_table_info, None)

        with self.assertRaises(Exception):
            read_batch = list(sqlengine.read(missing_table_info))
            self.assertEqual(read_batch, None)

        with self.assertRaises(Exception):
            sqlengine.delete(missing_table_info, None)

    def test_cannot_delete_missing_column(self):
        evadb = get_evadb_for_testing()
        sqlengine = SQLStorageEngine(evadb)
        sqlengine.create(self.table)

        incorrect_where_clause = {"foo": None}

        with self.assertRaises(Exception):
            sqlengine.delete(self.table, incorrect_where_clause)
        # clean up
        sqlengine.drop(self.table)

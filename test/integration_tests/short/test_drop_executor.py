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
from pathlib import Path
from test.util import create_sample_video, file_remove, get_evadb_for_testing

import pandas as pd
import pytest

from evadb.catalog.catalog_utils import get_video_table_column_definitions
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all
from evadb.storage.storage_engine import StorageEngine


@pytest.mark.notparallel
class DropObjectExecutorTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()
        self.video_file_path = create_sample_video()

    def tearDown(self):
        file_remove("dummy.avi")

    def _create_index(self, index_name):
        import numpy as np

        # Create feature vector table and raw input table.
        feat1 = np.array([[0, 0, 0]]).astype(np.float32)
        feat2 = np.array([[100, 100, 100]]).astype(np.float32)
        feat3 = np.array([[200, 200, 200]]).astype(np.float32)

        # Create table.
        execute_query_fetch_all(
            self.evadb,
            """create table if not exists testCreateIndexFeatTable (
                feat NDARRAY FLOAT32(1,3)
            );""",
        )

        # Create pandas dataframe.
        feat_batch_data = Batch(
            pd.DataFrame(
                data={
                    "feat": [feat1, feat2, feat3],
                }
            )
        )
        feat_tb_entry = self.evadb.catalog().get_table_catalog_entry(
            "testCreateIndexFeatTable"
        )
        storage_engine = StorageEngine.factory(self.evadb, feat_tb_entry)
        storage_engine.write(feat_tb_entry, feat_batch_data)

        query = (
            f"CREATE INDEX {index_name} ON testCreateIndexFeatTable (feat) USING FAISS;"
        )
        execute_query_fetch_all(self.evadb, query)

    # integration test
    def test_should_drop_table(self):
        query = f"""LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"""
        execute_query_fetch_all(self.evadb, query)

        # catalog should contain video table and the metadata table
        table_catalog_entry = self.evadb.catalog().get_table_catalog_entry("MyVideo")
        video_dir = table_catalog_entry.file_url
        self.assertFalse(table_catalog_entry is None)
        column_objects = self.evadb.catalog().get_column_catalog_entries_by_table(
            table_catalog_entry
        )
        # no of column objects should equal what we have defined plus one for row_id
        self.assertEqual(
            len(column_objects), len(get_video_table_column_definitions()) + 1
        )
        self.assertTrue(Path(video_dir).exists())
        video_metadata_table = (
            self.evadb.catalog().get_multimedia_metadata_table_catalog_entry(
                table_catalog_entry
            )
        )
        self.assertTrue(video_metadata_table is not None)

        drop_query = """DROP TABLE IF EXISTS MyVideo;"""
        execute_query_fetch_all(self.evadb, drop_query)
        self.assertTrue(self.evadb.catalog().get_table_catalog_entry("MyVideo") is None)
        column_objects = self.evadb.catalog().get_column_catalog_entries_by_table(
            table_catalog_entry
        )
        self.assertEqual(len(column_objects), 0)
        self.assertFalse(Path(video_dir).exists())

        # Fail if table already dropped
        drop_query = """DROP TABLE MyVideo;"""
        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(
                self.evadb, drop_query, do_not_print_exceptions=True
            )

        # we should be able to re-create the table
        execute_query_fetch_all(self.evadb, query)
        # clean up
        execute_query_fetch_all(self.evadb, drop_query)

    def run_create_function_query(self):
        create_function_query = """CREATE FUNCTION DummyObjectDetector
            INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
            OUTPUT (label NDARRAY STR(10))
            TYPE  Classification
            IMPL  'test/util.py';"""
        execute_query_fetch_all(self.evadb, create_function_query)

    def test_should_drop_function(self):
        self.run_create_function_query()
        function_name = "DummyObjectDetector"
        function = self.evadb.catalog().get_function_catalog_entry_by_name(
            function_name
        )
        self.assertTrue(function is not None)

        # Test that dropping the FUNCTION reflects in the catalog
        drop_query = "DROP FUNCTION IF EXISTS {};".format(function_name)
        execute_query_fetch_all(self.evadb, drop_query)
        function = self.evadb.catalog().get_function_catalog_entry_by_name(
            function_name
        )
        self.assertTrue(function is None)

        # We should be able to re-create the function
        self.run_create_function_query()
        # clean up
        execute_query_fetch_all(self.evadb, drop_query)

    def test_drop_wrong_function_name(self):
        self.run_create_function_query()
        right_function_name = "DummyObjectDetector"
        wrong_function_name = "FakeDummyObjectDetector"
        function = self.evadb.catalog().get_function_catalog_entry_by_name(
            right_function_name
        )
        self.assertTrue(function is not None)

        # Test that dropping the wrong FUNCTION:
        # - does not affect FUNCTIONs in the catalog
        # - raises an appropriate exception
        drop_query = "DROP FUNCTION {};".format(wrong_function_name)
        try:
            execute_query_fetch_all(
                self.evadb, drop_query, do_not_print_exceptions=True
            )
        except Exception as e:
            err_msg = "Function {} does not exist, therefore cannot be dropped.".format(
                wrong_function_name
            )
            self.assertTrue(str(e) == err_msg)
        function = self.evadb.catalog().get_function_catalog_entry_by_name(
            right_function_name
        )
        self.assertTrue(function is not None)

    #### DROP INDEX

    def test_should_drop_index(self):
        index_name = "index_name"
        self._create_index(index_name)

        index_obj = self.evadb.catalog().get_index_catalog_entry_by_name(index_name)
        self.assertTrue(index_obj is not None)

        # Test that dropping the wrong Index:
        # - does not affect Indexes in the catalog
        # - raises an appropriate exception
        wrong_function_name = "wrong_function_name"
        drop_query = f"DROP INDEX {wrong_function_name};"
        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(
                self.evadb, drop_query, do_not_print_exceptions=True
            )
        obj = self.evadb.catalog().get_index_catalog_entry_by_name(index_name)
        self.assertTrue(obj is not None)

        # Test that dropping the Index reflects in the catalog
        drop_query = f"DROP INDEX IF EXISTS {index_name};"
        execute_query_fetch_all(self.evadb, drop_query)
        index_obj = self.evadb.catalog().get_index_catalog_entry_by_name(index_name)
        self.assertTrue(index_obj is None)

        # todo check if the index is also removed from the underlying vector store

    #### DROP INDEX

    def test_should_drop_database(self):
        # Create database.
        database_name = "test_data_source"
        params = {
            "database": "evadb.db",
        }
        query = f"""CREATE DATABASE {database_name}
                    WITH ENGINE = "sqlite",
                    PARAMETERS = {params};"""
        execute_query_fetch_all(self.evadb, query)
        self.assertIsNotNone(
            self.evadb.catalog().get_database_catalog_entry(database_name)
        )

        # DROP DATABASE
        execute_query_fetch_all(self.evadb, f"DROP DATABASE {database_name}")
        self.assertIsNone(
            self.evadb.catalog().get_database_catalog_entry(database_name)
        )

        # DROP should pass with warning
        result = execute_query_fetch_all(
            self.evadb, f"DROP DATABASE IF EXISTS {database_name}"
        )
        self.assertTrue("does not exist" in result.frames.to_string())

        # DROP should throw error
        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(
                self.evadb,
                f"DROP DATABASE {database_name}",
                do_not_print_exceptions=True,
            )

        # We should be able to add the database again
        execute_query_fetch_all(self.evadb, query)

        # clean up
        result = execute_query_fetch_all(
            self.evadb, f"DROP DATABASE IF EXISTS {database_name}"
        )

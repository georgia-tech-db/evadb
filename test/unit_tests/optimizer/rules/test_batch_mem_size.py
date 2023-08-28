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
from test.util import get_evadb_for_testing

from mock import ANY, patch

from evadb.server.command_handler import execute_query_fetch_all
from evadb.storage.sqlite_storage_engine import SQLStorageEngine


class BatchMemSizeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        cls.evadb.catalog().reset()

    @classmethod
    def tearDownClass(cls):
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MyCSV;")

    def test_batch_mem_size_for_sqlite_storage_engine(self):
        """
            This testcase make sure that the `batch_mem_size` is correctly passed to
        the storage engine.
        """
        test_batch_mem_size = 100
        self.evadb.config.update_value(
            "executor", "batch_mem_size", test_batch_mem_size
        )
        create_table_query = """
            CREATE TABLE IF NOT EXISTS MyCSV (
                id INTEGER UNIQUE,
                frame_id INTEGER,
                video_id INTEGER,
                dataset_name TEXT(30),
                label TEXT(30),
                bbox NDARRAY FLOAT32(4),
                object_id INTEGER
            );"""
        execute_query_fetch_all(self.evadb, create_table_query)

        select_table_query = "SELECT * FROM MyCSV;"
        with patch.object(SQLStorageEngine, "read") as mock_read:
            mock_read.__iter__.return_value = []
            execute_query_fetch_all(self.evadb, select_table_query)
            mock_read.assert_called_with(ANY, test_batch_mem_size)

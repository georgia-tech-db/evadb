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
from test.util import (
    create_sample_csv,
    create_sample_video,
    file_remove,
    get_evadb_for_testing,
)

import pytest

from evadb.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class RenameExecutorTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()
        self.video_file_path = create_sample_video()
        self.csv_file_path = create_sample_csv()

    def tearDown(self):
        file_remove("dummy.avi")
        file_remove("dummy.csv")

    # integration test
    def test_should_rename_table(self):
        catalog_manager = self.evadb.catalog()
        query = f"""LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"""
        execute_query_fetch_all(self.evadb, query)

        self.assertTrue(catalog_manager.get_table_catalog_entry("MyVideo") is not None)
        self.assertTrue(catalog_manager.get_table_catalog_entry("MyVideo1") is None)

        rename_query = """RENAME TABLE MyVideo TO MyVideo1;"""
        execute_query_fetch_all(self.evadb, rename_query)

        self.assertTrue(catalog_manager.get_table_catalog_entry("MyVideo") is None)
        self.assertTrue(catalog_manager.get_table_catalog_entry("MyVideo1") is not None)
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyVideo;")

    # integration test
    def test_should_fail_on_rename_structured_table(self):
        # loading a csv requires a table to be created first
        create_table_query = """

            CREATE TABLE IF NOT EXISTS MyVideoCSV (
                id INTEGER UNIQUE,
                frame_id INTEGER NOT NULL,
                video_id INTEGER NOT NULL,
                dataset_name TEXT(30) NOT NULL
            );
            """
        execute_query_fetch_all(self.evadb, create_table_query)

        # load the CSV
        load_query = f"""LOAD CSV '{self.csv_file_path}' INTO MyVideoCSV (id, frame_id, video_id, dataset_name);"""
        execute_query_fetch_all(self.evadb, load_query)

        with self.assertRaises(Exception) as cm:
            rename_query = """RENAME TABLE MyVideoCSV TO MyVideoCSV1;"""
            execute_query_fetch_all(self.evadb, rename_query)

        self.assertEqual(
            str(cm.exception), "Rename not yet supported on structured data"
        )
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyVideoCSV;")

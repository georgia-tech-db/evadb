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
from test.util import (
    create_dummy_batches,
    create_dummy_csv_batches,
    create_sample_csv,
    create_sample_video,
    file_remove,
)

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all


class LoadExecutorTest(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        create_sample_video()
        create_sample_csv()

    def tearDown(self):
        file_remove("dummy.avi")
        file_remove("dummy.csv")

    # integration test for video
    def test_should_load_video_in_table(self):
        query = """LOAD FILE 'dummy.avi' INTO MyVideo
                   WITH FORMAT VIDEO;"""
        execute_query_fetch_all(query)

        select_query = """SELECT name, id, data FROM MyVideo;"""

        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())[0]
        self.assertEqual(actual_batch, expected_batch)

        # Try adding video to an existing table
        execute_query_fetch_all(query)
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(len(actual_batch), 2 * len(expected_batch))

    # integration tests for csv
    def test_should_load_csv_in_table(self):

        # loading a csv requires a table to be created first
        create_table_query = """

            CREATE TABLE IF NOT EXISTS MyVideoCSV (
                id INTEGER UNIQUE,
                frame_id INTEGER,
                video_id INTEGER,
                dataset_name TEXT(30),
                label TEXT(30),
                bbox NDARRAY FLOAT32(4),
                object_id INTEGER
            );

            """
        execute_query_fetch_all(create_table_query)

        # load the CSV
        load_query = """LOAD FILE 'dummy.csv' INTO MyVideoCSV
                   WITH FORMAT CSV;"""
        execute_query_fetch_all(load_query)

        # execute a select query
        select_query = """SELECT id, frame_id, video_id,
                          dataset_name, label, bbox,
                          object_id
                          FROM MyVideoCSV;"""

        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()

        # assert the batches are equal
        expected_batch = create_dummy_csv_batches()
        expected_batch.modify_column_alias("myvideocsv")
        self.assertEqual(actual_batch, expected_batch)

        # clean up
        drop_query = "DROP TABLE MyVideoCSV;"
        execute_query_fetch_all(drop_query)

    def test_should_load_csv_with_columns_in_table(self):

        # loading a csv requires a table to be created first
        create_table_query = """

            CREATE TABLE IF NOT EXISTS MyVideoCSV (
                id INTEGER UNIQUE,
                frame_id INTEGER NOT NULL,
                video_id INTEGER NOT NULL,
                dataset_name TEXT(30) NOT NULL
            );
            """
        execute_query_fetch_all(create_table_query)

        # load the CSV
        load_query = """LOAD FILE 'dummy.csv' INTO MyVideoCSV (id, frame_id, video_id, dataset_name)
                   WITH FORMAT CSV;"""
        execute_query_fetch_all(load_query)

        # execute a select query
        select_query = """SELECT id, frame_id, video_id, dataset_name
                          FROM MyVideoCSV;"""

        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()

        # assert the batches are equal
        select_columns = ["id", "frame_id", "video_id", "dataset_name"]
        expected_batch = create_dummy_csv_batches(target_columns=select_columns)
        expected_batch.modify_column_alias("myvideocsv")
        self.assertEqual(actual_batch, expected_batch)

        # clean up
        drop_query = "DROP TABLE MyVideoCSV;"
        execute_query_fetch_all(drop_query)

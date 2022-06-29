# coding=utf-8
# Copyright 2018-2020 EVA
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

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all
from test.util import create_sample_video, create_sample_csv
from test.util import create_dummy_batches, create_dummy_csv_batches
from test.util import file_remove


class LoadExecutorTest(unittest.TestCase):

    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        create_sample_video()
        create_sample_csv()

    def tearDown(self):
        file_remove('dummy.avi')
        file_remove('dummy.csv')

    # integration test for video
    def test_should_load_video_in_table(self):
        query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo
                   WITH FORMAT VIDEO;"""
        execute_query_fetch_all(query)

        select_query = """SELECT id, data FROM MyVideo;"""

        actual_batch = sorted(execute_query_fetch_all(select_query))
        expected_batch = list(create_dummy_batches())[0]
        expected_batch.modify_column_alias('myvideo')
        self.assertEqual(actual_batch, expected_batch)

    # integration test for csv
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
        load_query = """LOAD DATA INFILE 'dummy.csv' INTO MyVideoCSV
                   WITH FORMAT CSV;"""
        execute_query_fetch_all(load_query)

        # execute a select query
        select_query = """SELECT id, frame_id, video_id,
                          dataset_name, label, bbox,
                          object_id
                          FROM MyVideoCSV;"""

        actual_batch = sorted(execute_query_fetch_all(select_query))

        # assert the batches are equal
        expected_batch = create_dummy_csv_batches()
        expected_batch.modify_column_alias('myvideocsv')
        self.assertEqual(actual_batch, expected_batch)

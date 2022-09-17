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
import base64
import os
import unittest
from test.util import (
    create_dummy_batches,
    create_dummy_csv_batches,
    create_sample_csv_as_blob,
    create_sample_video_as_blob,
    file_remove,
    upload_dir_from_config,
)

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all


class UploadExecutorTest(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        self.video_blob = create_sample_video_as_blob()
        self.csv_blob = create_sample_csv_as_blob()

    def tearDown(self):
        file_remove("dummy.avi")
        file_remove("dummy.csv")

    # integration test
    def test_should_upload_file_to_location(self):
        query = (
            'UPLOAD PATH "dummy.avi" BLOB '
            + '"'
            + self.video_blob
            + '" '
            + "INTO MyVideo WITH FORMAT VIDEO;"
        )
        execute_query_fetch_all(query)
        expected_blob = self.video_blob
        with open(os.path.join(upload_dir_from_config, "dummy.avi"), "rb") as f:
            bytes_read = f.read()
            actual_blob = str(base64.b64encode(bytes_read))
        self.assertEqual(actual_blob, expected_blob)

    def test_should_upload_file_to_location_without_format(self):
        query = (
            'UPLOAD PATH "dummy.avi" BLOB '
            + '"'
            + self.video_blob
            + '" '
            + "INTO MyVideo;"
        )
        execute_query_fetch_all(query)
        expected_blob = self.video_blob
        with open(os.path.join(upload_dir_from_config, "dummy.avi"), "rb") as f:
            bytes_read = f.read()
            actual_blob = str(base64.b64encode(bytes_read))
        self.assertEqual(actual_blob, expected_blob)

    # integration test for video
    def test_should_upload_video_to_table(self):
        query = (
            'UPLOAD PATH "dummy.avi" BLOB '
            + '"'
            + self.video_blob
            + '" '
            + "INTO MyVideo WITH FORMAT VIDEO;"
        )
        execute_query_fetch_all(query)

        select_query = """SELECT name, id, data FROM MyVideo;"""

        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())[0]
        expected_batch.modify_column_alias("myvideo")
        self.assertEqual(actual_batch, expected_batch)

    # integration test for csv
    def test_should_upload_csv_to_table(self):
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
        query = (
            'UPLOAD PATH "dummy.csv" BLOB '
            + '"'
            + self.csv_blob
            + '" '
            + "INTO MyVideoCSV WITH FORMAT CSV;"
        )
        execute_query_fetch_all(query)

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

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
from test.util import (
    create_sample_csv,
    create_sample_video,
    file_remove,
    get_evadb_for_testing,
    shutdown_ray,
)

import pytest

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.server.command_handler import execute_query_fetch_all
from evadb.udfs.udf_bootstrap_queries import fuzzy_udf_query


@pytest.mark.notparallel
class FuzzyJoinTests(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        self.video_file_path = create_sample_video()
        self.image_files_path = Path(
            f"{EvaDB_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/*.jpg"
        )
        self.csv_file_path = create_sample_csv()

        # Prepare needed UDFs and data.
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
        execute_query_fetch_all(self.evadb, create_table_query)

        # load the CSV
        load_query = f"LOAD CSV '{self.csv_file_path}' INTO MyVideoCSV;"
        execute_query_fetch_all(self.evadb, load_query)

        # load the video to be joined with the csv
        query = f"LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(self.evadb, query)

    def tearDown(self):
        shutdown_ray()

        file_remove("dummy.avi")
        file_remove("dummy.csv")
        # clean up
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyVideo;")
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyVideoCSV;")

    def test_fuzzyjoin(self):
        execute_query_fetch_all(self.evadb, fuzzy_udf_query)

        # TODO this test does not make sense. Need to improve
        fuzzy_join_query = """SELECT * FROM MyVideo a JOIN MyVideoCSV b
                      ON FuzzDistance(a.id, b.id) = 100;"""

        actual_batch = execute_query_fetch_all(self.evadb, fuzzy_join_query)
        self.assertEqual(len(actual_batch), 10)

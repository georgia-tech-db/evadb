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
from pathlib import Path
from test.util import create_sample_csv, create_sample_video, file_remove, shutdown_ray

import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.server.command_handler import execute_query_fetch_all

EVA_INSTALLATION_DIR = ConfigurationManager().get_value("core", "eva_installation_dir")


@pytest.mark.notparallel
class FuzzyJoinTests(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        self.video_file_path = create_sample_video()
        self.image_files_path = Path(
            f"{EVA_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/*.jpg"
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
        execute_query_fetch_all(create_table_query)

        # load the CSV
        load_query = f"LOAD CSV '{self.csv_file_path}' INTO MyVideoCSV;"
        execute_query_fetch_all(load_query)

        # load the video to be joined with the csv
        query = f"LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(query)

    def tearDown(self):
        shutdown_ray()

        file_remove("dummy.avi")
        file_remove("dummy.csv")
        # clean up
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideoCSV;")

    def test_fuzzyjoin(self):
        fuzzy_udf = """CREATE UDF IF NOT EXISTS FuzzDistance
                    INPUT (Input_Array1 NDARRAY ANYTYPE, Input_Array2 NDARRAY ANYTYPE)
                    OUTPUT (distance FLOAT(32, 7))
                    TYPE NdarrayUDF
                    IMPL "{}/udfs/{}/fuzzy_join.py";
        """.format(
            EVA_INSTALLATION_DIR, "ndarray"
        )
        execute_query_fetch_all(fuzzy_udf)

        fuzzy_join_query = """SELECT * FROM MyVideo a JOIN MyVideoCSV b
                      ON FuzzDistance(a.id, b.id) = 100;"""

        actual_batch = execute_query_fetch_all(fuzzy_join_query)
        self.assertEqual(len(actual_batch), 10)

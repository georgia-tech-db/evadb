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
    create_sample_video,
    file_remove,
    get_evadb_for_testing,
    shutdown_ray,
)

import numpy as np
import pandas as pd
import pytest

from evadb.server.command_handler import execute_query_fetch_all
from evadb.utils.logging_manager import logger


@pytest.mark.notparallel
class InsertExecutorTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()
        self.video_file_path = create_sample_video()

        query = """CREATE TABLE IF NOT EXISTS CSVTable
            (
                name TEXT(100)
            );
        """
        execute_query_fetch_all(self.evadb, query)

    def tearDown(self):
        shutdown_ray()
        file_remove("dummy.avi")

    # integration test
    @unittest.skip("Not supported in current version")
    def test_should_load_video_in_table(self):
        query = f"""LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"""
        execute_query_fetch_all(self.evadb, query)

        insert_query = """ INSERT INTO MyVideo (id, data) VALUES
            (40, [[40, 40, 40], [40, 40, 40]],
                 [[40, 40, 40], [40, 40, 40]]);"""
        execute_query_fetch_all(self.evadb, insert_query)

        insert_query_2 = """ INSERT INTO MyVideo (id, data) VALUES
        ( 41, [[41, 41, 41] , [41, 41, 41]],
                [[41, 41, 41], [41, 41, 41]]);"""
        execute_query_fetch_all(self.evadb, insert_query_2)

        query = "SELECT id, data FROM MyVideo WHERE id = 40"
        batch = execute_query_fetch_all(self.evadb, query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[40, 40, 40], [40, 40, 40]], [[40, 40, 40], [40, 40, 40]]]),
            )
        )

        query = "SELECT id, data FROM MyVideo WHERE id = 41;"
        batch = execute_query_fetch_all(self.evadb, query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[41, 41, 41], [41, 41, 41]], [[41, 41, 41], [41, 41, 41]]]),
            )
        )

    def test_should_insert_tuples_in_table(self):
        data = pd.read_csv("./test/data/features.csv")
        for i in data.iterrows():
            logger.info(i[1][1])
            query = f"""INSERT INTO CSVTable (name) VALUES (
                            '{i[1][1]}'
                        );"""
            logger.info(query)
            batch = execute_query_fetch_all(self.evadb, query)

        query = "SELECT name FROM CSVTable;"
        batch = execute_query_fetch_all(self.evadb, query)
        logger.info(batch)

        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["csvtable.name"].array,
                np.array(
                    [
                        "test_evadb/similarity/data/sad.jpg",
                        "test_evadb/similarity/data/happy.jpg",
                        "test_evadb/similarity/data/angry.jpg",
                    ]
                ),
            )
        )

        query = """SELECT name FROM CSVTable WHERE name LIKE '.*(sad|happy)';"""
        batch = execute_query_fetch_all(self.evadb, query)
        self.assertEqual(len(batch._frames), 2)

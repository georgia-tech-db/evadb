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
    file_remove,
    get_evadb_for_testing,
    load_udfs_for_testing,
    shutdown_ray,
)

import numpy as np
import pytest

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class DeleteExecutorTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        load_udfs_for_testing(self.evadb, mode="debug")

        create_table_query = """
                CREATE TABLE IF NOT EXISTS testDeleteOne
                (
                 id INTEGER,
                 dummyfloat FLOAT(5, 3),
                 feat   NDARRAY FLOAT32(1, 3),
                 input  NDARRAY UINT8(1, 3)
                 );
                """
        execute_query_fetch_all(self.evadb, create_table_query)

        insert_query1 = """
                INSERT INTO testDeleteOne (id, dummyfloat, feat, input)
                VALUES (5, 1.5, [[0, 0, 0]], [[0, 0, 0]]);
        """
        execute_query_fetch_all(self.evadb, insert_query1)
        insert_query2 = """
                INSERT INTO testDeleteOne (id, dummyfloat,feat, input)
                VALUES (15, 2.5, [[100, 100, 100]], [[100, 100, 100]]);
        """
        execute_query_fetch_all(self.evadb, insert_query2)
        insert_query3 = """
                INSERT INTO testDeleteOne (id, dummyfloat,feat, input)
                VALUES (25, 3.5, [[200, 200, 200]], [[200, 200, 200]]);
        """
        execute_query_fetch_all(self.evadb, insert_query3)

        ####################################################
        # Create a table for testing Delete with Video Data#
        ####################################################

        path = f"{EvaDB_ROOT_DIR}/data/sample_videos/1/*.mp4"
        query = f'LOAD VIDEO "{path}" INTO TestDeleteVideos;'
        _ = execute_query_fetch_all(self.evadb, query)

    def tearDown(self):
        shutdown_ray()
        file_remove("dummy.avi")

    # integration test
    @unittest.skip("Not supported in current version")
    def test_should_delete_single_video_in_table(self):
        path = f"{EvaDB_ROOT_DIR}/data/sample_videos/1/2.mp4"
        delete_query = f"""DELETE FROM TestDeleteVideos WHERE name="{path}";"""
        batch = execute_query_fetch_all(self.evadb, delete_query)

        query = "SELECT name FROM MyVideo"
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

    @unittest.skip("Not supported in current version")
    def test_should_delete_single_image_in_table(self):
        path = f"{EvaDB_ROOT_DIR}/data/sample_videos/1/2.mp4"
        delete_query = f"""DELETE FROM TestDeleteVideos WHERE name="{path}";"""
        batch = execute_query_fetch_all(self.evadb, delete_query)

        query = "SELECT name FROM MyVideo"
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

    def test_should_delete_tuple_in_table(self):
        delete_query = """DELETE FROM testDeleteOne WHERE
               id < 20 OR dummyfloat < 2 AND id < 5 AND 20 > id
               AND id <= 20 AND id >= 5 OR id != 15 OR id = 15;"""
        batch = execute_query_fetch_all(self.evadb, delete_query)

        query = "SELECT * FROM testDeleteOne;"
        batch = execute_query_fetch_all(self.evadb, query)

        np.testing.assert_array_equal(
            batch.frames["testdeleteone.id"].array,
            np.array([25], dtype=np.int64),
        )

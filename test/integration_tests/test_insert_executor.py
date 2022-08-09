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
from test.util import create_sample_video, file_remove

import numpy as np

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all


class InsertExecutorTest(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        create_sample_video()

    def tearDown(self):
        file_remove("dummy.avi")

    # integration test
    @unittest.skip("Not supported in current version")
    def test_should_load_video_in_table(self):
        query = """LOAD FILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(query)

        insert_query = """ INSERT INTO MyVideo (id, data) VALUES (40,
                            [[[40, 40, 40] , [40, 40, 40]],
                            [[40, 40, 40], [40, 40, 40]]]);"""
        execute_query_fetch_all(insert_query)

        insert_query_2 = """ INSERT INTO MyVideo (id, data) VALUES (41,
                            [[[41, 41, 41] , [41, 41, 41]],
                            [[41, 41, 41], [41, 41, 41]]]);"""
        execute_query_fetch_all(insert_query_2)

        query = "SELECT id, data FROM MyVideo WHERE id = 40"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[40, 40, 40], [40, 40, 40]], [[40, 40, 40], [40, 40, 40]]]),
            )
        )

        query = "SELECT id, data FROM MyVideo WHERE id = 41;"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[41, 41, 41], [41, 41, 41]], [[41, 41, 41], [41, 41, 41]]]),
            )
        )

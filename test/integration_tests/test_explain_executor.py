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
from test.util import create_sample_video, create_table, file_remove, load_inbuilt_udfs

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


class ExplainExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)
        load_query = """LOAD FILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(load_query)
        load_inbuilt_udfs()
        cls.table1 = create_table("table1", 100, 3)
        cls.table2 = create_table("table2", 500, 3)
        cls.table3 = create_table("table3", 1000, 3)

    @classmethod
    def tearDownClass(cls):
        file_remove("dummy.avi")
        drop_query = """DROP TABLE table1;"""
        execute_query_fetch_all(drop_query)
        drop_query = """DROP TABLE table2;"""
        execute_query_fetch_all(drop_query)
        drop_query = """DROP TABLE table3;"""
        execute_query_fetch_all(drop_query)

    def test_explain_simple_select(self):
        select_query = "EXPLAIN SELECT id, data FROM MyVideo"
        batch = execute_query_fetch_all(select_query)
        expected_output = """|__ SeqScanPlan\n    |__ StoragePlan\n"""
        self.assertEqual(batch.frames[0][0], expected_output)

        select_query = "EXPLAIN SELECT id, data FROM MyVideo JOIN LATERAL DummyObjectDetector(data) AS T ;"
        batch = execute_query_fetch_all(select_query)
        expected_output = """|__ ProjectPlan\n    |__ LateralJoinPlan\n        |__ SeqScanPlan\n            |__ StoragePlan\n        |__ FunctionScanPlan\n"""
        self.assertEqual(batch.frames[0][0], expected_output)

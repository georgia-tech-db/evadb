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
import os
import unittest
from test.markers import windows_skip_marker
from test.util import get_evadb_for_testing

import pandas as pd
import pytest

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all
from evadb.udfs.udf_bootstrap_queries import ArrayCount_udf_query, Fastrcnn_udf_query

NUM_FRAMES = 10


@pytest.mark.notparallel
class ShowExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()
        queries = [Fastrcnn_udf_query, ArrayCount_udf_query]
        for query in queries:
            execute_query_fetch_all(cls.evadb, query)

        ua_detrac = f"{EvaDB_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        mnist = f"{EvaDB_ROOT_DIR}/data/mnist/mnist.mp4"
        actions = f"{EvaDB_ROOT_DIR}/data/actions/actions.mp4"
        execute_query_fetch_all(cls.evadb, f"LOAD VIDEO '{ua_detrac}' INTO MyVideo;")
        execute_query_fetch_all(cls.evadb, f"LOAD VIDEO '{mnist}' INTO MNIST;")
        execute_query_fetch_all(cls.evadb, f"LOAD VIDEO '{actions}' INTO Actions;")

    @classmethod
    def tearDownClass(cls):
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS Actions;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MNIST;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MyVideo;")

    # integration test
    def test_show_udfs(self):
        result = execute_query_fetch_all(self.evadb, "SHOW UDFS;")
        self.assertEqual(len(result.columns), 6)

        expected = {
            "name": ["FastRCNNObjectDetector", "ArrayCount"],
            "type": ["Classification", "NdarrayUDF"],
        }
        expected_df = pd.DataFrame(expected)
        self.assertTrue(all(expected_df.name == result.frames.name))
        self.assertTrue(all(expected_df.type == result.frames.type))

    @windows_skip_marker
    def test_show_tables(self):
        # Note this test can causes sqlalchemy issues if the evadb_server is not stopped
        result = execute_query_fetch_all(self.evadb, "SHOW TABLES;")
        self.assertEqual(len(result), 3)
        expected = {"name": ["MyVideo", "MNIST", "Actions"]}
        expected_df = pd.DataFrame(expected)
        self.assertEqual(result, Batch(expected_df))

        # Stop and restart server
        os.system("nohup evadb_server --stop")
        os.system("nohup evadb_server --start &")

        result = execute_query_fetch_all(self.evadb, "SHOW TABLES;")
        self.assertEqual(len(result), 3)
        expected = {"name": ["MyVideo", "MNIST", "Actions"]}
        expected_df = pd.DataFrame(expected)
        self.assertEqual(result, Batch(expected_df))

        # stop the server
        os.system("nohup evadb_server --stop")

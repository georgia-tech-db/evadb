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
import os
import sys
import unittest

import pandas as pd
import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all
from eva.udfs.udf_bootstrap_queries import ArrayCount_udf_query, Fastrcnn_udf_query

NUM_FRAMES = 10


class ShowExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        queries = [Fastrcnn_udf_query, ArrayCount_udf_query]
        for query in queries:
            execute_query_fetch_all(query)

        ua_detrac = f"{EVA_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        mnist = f"{EVA_ROOT_DIR}/data/mnist/mnist.mp4"
        actions = f"{EVA_ROOT_DIR}/data/actions/actions.mp4"
        execute_query_fetch_all(f"LOAD VIDEO '{ua_detrac}' INTO MyVideo;")
        execute_query_fetch_all(f"LOAD VIDEO '{mnist}' INTO MNIST;")
        execute_query_fetch_all(f"LOAD VIDEO '{actions}' INTO Actions;")

    @classmethod
    def tearDownClass(cls):
        execute_query_fetch_all("DROP TABLE IF EXISTS Actions;")
        execute_query_fetch_all("DROP TABLE IF EXISTS Mnist;")
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

    # integration test
    def test_show_udfs(self):
        result = execute_query_fetch_all("SHOW UDFS;")
        self.assertEqual(len(result.columns), 5)

        expected = {
            "name": ["FastRCNNObjectDetector", "Array_Count"],
            "inputs": [
                ["Frame_Array NDARRAY UINT8 (3, None, None)"],
                ["Input_Array NDARRAY ANYTYPE ()", "Search_Key ANY"],
            ],
            "outputs": [
                [
                    "labels NDARRAY STR (None,)",
                    "bboxes NDARRAY FLOAT32 (None, 4)",
                    "scores NDARRAY FLOAT32 (None,)",
                ],
                ["key_count INTEGER"],
            ],
            "type": ["Classification", "NdarrayUDF"],
        }
        expected_df = pd.DataFrame(expected)
        self.assertTrue(all(expected_df.inputs == result.frames.inputs))
        self.assertTrue(all(expected_df.outputs == result.frames.outputs))
        self.assertTrue(all(expected_df.name == result.frames.name))
        self.assertTrue(all(expected_df.type == result.frames.type))

    @pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
    def test_show_tables(self):

        result = execute_query_fetch_all("SHOW TABLES;")
        self.assertEqual(len(result), 3)
        expected = {"name": ["MyVideo", "MNIST", "Actions"]}
        expected_df = pd.DataFrame(expected)
        self.assertEqual(result, Batch(expected_df))

        # Stop and restart server
        os.system("nohup eva_server --stop")
        os.system("nohup eva_server --start &")

        result = execute_query_fetch_all("SHOW TABLES;")
        self.assertEqual(len(result), 3)
        expected = {"name": ["MyVideo", "MNIST", "Actions"]}
        expected_df = pd.DataFrame(expected)
        self.assertEqual(result, Batch(expected_df))

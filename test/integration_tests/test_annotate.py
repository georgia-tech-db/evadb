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
from test.util import (
    NUM_FRAMES,
    create_sample_video,
    file_remove,
    load_udfs_for_testing,
)

import pandas as pd
import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all

class ArrayCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        ua_detrac = f"{EVA_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        execute_query_fetch_all(f"LOAD VIDEO '{ua_detrac}' INTO MyVideo;")
        load_udfs_for_testing(mode="minimal")

    @classmethod
    def tearDownClass(cls):
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")
        file_remove("dummy.avi")

    def test_annotate_image_integration_test(self):
        select_query = """SELECT Annotate(data, FastRCNNObjectDetector(data))
            FROM MyVideo;"""

        # select_query = """SELECT FastRCNNObjectDetector(data)
        #     FROM MyVideo;"""
        
        actual_batch = execute_query_fetch_all(select_query)

        print(actual_batch)
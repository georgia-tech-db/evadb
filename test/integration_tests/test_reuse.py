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
    create_dummy_batches,
    create_sample_video,
    create_table,
    file_remove,
    load_inbuilt_udfs,
)

import numpy as np
import pandas as pd
import pytest

from eva.binder.binder_utils import BinderError
from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.readers.opencv_reader import OpenCVReader
from eva.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


class ReuseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        #create_sample_video(NUM_FRAMES)
        load_query = """LOAD FILE './data/top_gun.mp4' INTO top_gun;"""
        execute_query_fetch_all(load_query)
        load_inbuilt_udfs()
        #cls.table1 = create_table("table1", 100, 3)
        #cls.table2 = create_table("table2", 500, 3)
        #cls.table3 = create_table("table3", 1000, 3)

    @classmethod
    def tearDownClass(cls):
        #file_remove("dummy.avi")
        pass

    def test_query_1(self):
        select_query = """SELECT id, bbox FROM top_gun JOIN 
                        LATERAL FastRCNNObjectDetector(data) AS Obj(bbox, conf, label) WHERE id < 100;"""

        actual_batch = execute_query_fetch_all(select_query)
        print(f"actual_batch: {actual_batch}")

        # assert false
        self.assertEqual(1 == 1, False)

    def test_query_2(self):
        select_query = """SELECT id, bbox FROM top_gun JOIN 
                        LATERAL FastRCNNObjectDetector(data) AS Obj(bbox, conf, label) WHERE id < 200;"""

        actual_batch = execute_query_fetch_all(select_query)
        print(f"actual_batch: {actual_batch}")

        # assert false
        self.assertEqual(1 == 1, False)

    def test_query_3(self):
        select_query = """SELECT id, bbox FROM top_gun JOIN 
                        LATERAL FastRCNNObjectDetector(data) AS Obj(bbox, conf, label) WHERE id < 300;"""

        actual_batch = execute_query_fetch_all(select_query)
        print(f"actual_batch: {actual_batch}")

        # assert false
        self.assertEqual(1 == 1, False)


if __name__ == "__main__":
    unittest.main()

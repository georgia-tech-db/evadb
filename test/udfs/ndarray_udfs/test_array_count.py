# coding=utf-8
# Copyright 2018-2020 EVA
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
import pandas as pd

from src.catalog.catalog_manager import CatalogManager
from src.models.storage.batch import Batch
from src.udfs.ndarray_udfs.array_count import Array_Count
from test.util import perform_query
from test.util import populate_catalog_with_built_in_udfs


class ArrayCountTests(unittest.TestCase):

    def setUp(self):
        CatalogManager().reset()
        populate_catalog_with_built_in_udfs()

        load_query = """LOAD DATA INFILE 'data/ua_detrac/ua_detrac.mp4'
                        INTO MyVideo;"""
        perform_query(load_query)

    def test_should_return_count(self):
        query = """SELECT FastRCNNObjectDetector(data).labels FROM MyVideo WHERE id < 2;"""
        obj_det_batch = perform_query(query)

        print(obj_det_batch.frames.shape)

        # ac = Array_Count(obj_det_batch.frames, "car")
        # print(ac.name)
        # print(ac.exec(obj_det_batch.frames))

        query = """SELECT Array_Count(FastRCNNObjectDetector(data).labels, "car") FROM MyVideo WHERE id < 2;"""

        array_count_result = perform_query(query)
        print(array_count_result)

        select_query = """SELECT FastRCNNObjectDetector(data) FROM MyVideo WHERE id < 5;"""
        actual_batch = perform_query(select_query)
        self.assertEqual(actual_batch.batch_size, 5)


if __name__ == "__main__":
    unittest.main()

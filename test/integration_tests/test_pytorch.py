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

from src.catalog.catalog_manager import CatalogManager
from test.util import perform_query


class PytorchTest(unittest.TestCase):

    def setUp(self):
        CatalogManager().reset()

    def test_should_run_pytorch_and_fastrcnn(self):
        query = """LOAD DATA INFILE 'data/ua_detrac/ua_detrac.mp4'
                   INTO MyVideo;"""
        perform_query(query)

        create_udf_query = """CREATE UDF FastRCNNObjectDetector
                  INPUT  (Frame_Array NDARRAY (3, 256, 256))
                  OUTPUT (label TEXT(10))
                  TYPE  Classification
                  IMPL  'src/udfs/fastrcnn_object_detector.py';
        """
        perform_query(create_udf_query)

        select_query = """SELECT FastRCNNObjectDetector(data) FROM MyVideo
                        WHERE id < 5;"""
        actual_batch = perform_query(select_query)
        self.assertEqual(actual_batch.batch_size, 5)

    def test_should_run_pytorch_and_ssd(self):
        query = """LOAD DATA INFILE 'data/ua_detrac/ua_detrac.mp4'
                   INTO MyVideo;"""
        perform_query(query)

        create_udf_query = """CREATE UDF SSDObjectDetector
                  INPUT  (Frame_Array NDARRAY (3, 256, 256))
                  OUTPUT (label TEXT(10))
                  TYPE  Classification
                  IMPL  'src/udfs/ssd_object_detector.py';
        """
        perform_query(create_udf_query)

        select_query = """SELECT SSDObjectDetector(data) FROM MyVideo
                        WHERE id < 5;"""
        actual_batch = perform_query(select_query)
        self.assertEqual(actual_batch.batch_size, 5)

        # non-trivial test case
        res = actual_batch.frames
        for idx in res.index:
            self.assertTrue('car' in res['label'][idx])

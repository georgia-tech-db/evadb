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

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all

from test.util import copy_sample_video_to_prefix, file_remove


class PytorchTest(unittest.TestCase):

    def setUp(self):
        CatalogManager().reset()
        copy_sample_video_to_prefix()

    def tearDown(self):
        file_remove('ua_detrac.mp4')

    def test_should_run_pytorch_and_fastrcnn(self):
        query = """LOAD DATA INFILE 'ua_detrac.mp4'
                   INTO MyVideo;"""
        execute_query_fetch_all(query)

        create_udf_query = """CREATE UDF FastRCNNObjectDetector
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'src/udfs/fastrcnn_object_detector.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT FastRCNNObjectDetector(data) FROM MyVideo
                        WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(actual_batch.batch_size, 5)

    def test_should_run_pytorch_and_ssd(self):
        query = """LOAD DATA INFILE 'ua_detrac.mp4'
                   INTO MyVideo;"""
        execute_query_fetch_all(query)

        create_udf_query = """CREATE UDF SSDObjectDetector
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'src/udfs/ssd_object_detector.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT SSDObjectDetector(data) FROM MyVideo
                        WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(actual_batch.batch_size, 5)

        # non-trivial test case
        res = actual_batch.frames
        for idx in res.index:
            self.assertTrue('car' in res['label'][idx])

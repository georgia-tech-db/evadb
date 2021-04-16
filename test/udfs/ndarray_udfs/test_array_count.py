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
import os
import pandas as pd

from src.catalog.catalog_manager import CatalogManager
from src.models.storage.batch import Batch
from src.server.command_handler import execute_query_fetch_all
from src.udfs.ndarray_udfs.array_count import Array_Count
from test.util import create_sample_video, create_dummy_batches, \
    DummyObjectDetector
# from test.util import populate_catalog_with_built_in_udfs

from src.udfs.ndarray_udfs.create_ndarray_udf_queries import \
    DummyObjectDetector_udf_query, ArrayCount_udf_query

NUM_FRAMES = 10


class ArrayCountTests(unittest.TestCase):

    def setUp(self):
        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(load_query)

        create_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """
        execute_query_fetch_all(create_udf_query)

        ArrayCount_udf_query = """CREATE UDF Array_Count
                    INPUT(frame_data NDARRAY UINT8(3, 256, 256), label TEXT(10))
                    OUTPUT(count INTEGER)
                    TYPE Ndarray
                    IMPL "src/udfs/ndarray_udfs/array_count.py";
        """

        execute_query_fetch_all(ArrayCount_udf_query)

        fastrcnn_udf = """CREATE UDF FastRCNNObjectDetector
                      INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                      OUTPUT (labels NDARRAY STR(10), bboxes NDARRAY FLOAT32(10),
                                scores NDARRAY FLOAT3   2(10))
                      TYPE  Classification
                      IMPL  'src/udfs/fastrcnn_object_detector.py';
                      """
        execute_query_fetch_all(fastrcnn_udf)


    def tearDown(self):
        os.remove('dummy.avi')

    # integration test

    def test_should_load_and_select_using_udf_video_in_table(self):
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        labels = DummyObjectDetector().labels
        expected = [{'id': i, 'label': [labels[1 + i % 2]]}
                    for i in range(NUM_FRAMES)]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

    def test_should_load_and_select_using_udf_video(self):
        # Equality test
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE DummyObjectDetector(data).label = ['person'] ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        expected = [{'id': i * 2, 'label': ['person']}
                    for i in range(NUM_FRAMES // 2)]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

        # Contain test
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE DummyObjectDetector(data).label @> ['person'] ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(actual_batch, expected_batch)

    def test_array_count(self):
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo;"
        actual_batch = execute_query_fetch_all(select_query)
        print(actual_batch.frames)
        print(actual_batch.frames.shape)
        print(actual_batch.frames.dtypes)

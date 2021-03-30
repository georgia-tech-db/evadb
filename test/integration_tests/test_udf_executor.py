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

from test.util import create_sample_video, create_dummy_batches, \
    DummyObjectDetector

NUM_FRAMES = 10


class UDFExecutorTest(unittest.TestCase):

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

        # Mutli element contain test

        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE DummyObjectDetector(data).label <@ ['person', 'bicycle'] \
            ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        expected = [{'id': i * 2, 'label': ['person']}
                    for i in range(NUM_FRAMES // 2)]
        expected += [{'id': i, 'label': ['bicycle']}
                     for i in range(NUM_FRAMES)
                     if i % 2 + 1 == 2]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        expected_batch.sort()
        self.assertEqual(actual_batch, expected_batch)

        nested_select_query = """SELECT id, data FROM
            (SELECT id, data, DummyObjectDetector(data) FROM MyVideo
                WHERE id >= 2
            )
            WHERE ['person'] <@ label;
            """
        actual_batch = execute_query_fetch_all(nested_select_query)
        actual_batch.sort()
        expected_batch = list(
            create_dummy_batches(
                filters=[i
                         for i in range(2, NUM_FRAMES)
                         if i % 2 == 0]))[0]
        self.assertEqual(actual_batch, expected_batch)


if __name__ == '__main__':
    unittest.main()

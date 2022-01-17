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
from src.server.command_handler import execute_query_fetch_all
from test.util import create_sample_video, file_remove, \
    copy_sample_video_to_prefix
from test.util import DummyObjectDetector

NUM_FRAMES = 10


class MaterializedViewTest(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        create_sample_video()
        copy_sample_video_to_prefix()
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(load_query)

        create_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY (3, 256, 256))
                  OUTPUT (label TEXT(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """
        execute_query_fetch_all(create_udf_query)

    def tearDown(self):
        file_remove('dummy.avi')
        file_remove('ua_detrac.mp4')

    def test_should_mat_view_with_dummy(self):
        materialized_query = """CREATE MATERIALIZED VIEW dummy_view (id, label)
            AS SELECT id, DummyObjectDetector(data).label FROM MyVideo;
        """
        execute_query_fetch_all(materialized_query)

        select_query = 'SELECT id, label FROM dummy_view;'
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()

        labels = DummyObjectDetector().labels
        expected = [{'id': i, 'label': labels[1 + i % 2]}
                    for i in range(NUM_FRAMES)]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

    def test_should_mat_view_to_the_same_table(self):
        materialized_query = """CREATE MATERIALIZED VIEW IF NOT EXISTS
            dummy_view2 (id, label)
            AS SELECT id, DummyObjectDetector(data).label FROM MyVideo
            WHERE id < 5;
        """
        execute_query_fetch_all(materialized_query)

        materialized_query = """CREATE MATERIALIZED VIEW IF NOT EXISTS
            dummy_view2 (id, label)
            AS SELECT id, DummyObjectDetector(data).label FROM MyVideo
            WHERE id >= 5;
        """
        execute_query_fetch_all(materialized_query)

        select_query = 'SELECT id, label FROM dummy_view2;'
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()

        labels = DummyObjectDetector().labels
        expected = [{'id': i, 'label': labels[1 + i % 2]}
                    for i in range(5)]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

    # @unittest.skip('Too slow when no GPU')
    def test_should_mat_view_with_aafastrcnn(self):
        query = """LOAD DATA INFILE 'ua_detrac.mp4'
                   INTO MyVideo;"""
        execute_query_fetch_all(query)

        create_udf_query = """CREATE UDF FastRCNNObjectDetector
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(ANYDIM),
                          bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  Classification
                  IMPL  'src/udfs/fastrcnn_object_detector.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT id, FastRCNNObjectDetector(data).labels
                            FROM MyVideo WHERE id < 5;"""
        query = '''CREATE MATERIALIZED VIEW uadtrac_fastRCNN (id, labels) \
        AS {}'''.format(select_query)
        execute_query_fetch_all(query)

        select_view_query = 'SELECT id, labels FROM uadtrac_fastRCNN'
        actual_batch = execute_query_fetch_all(select_view_query)
        actual_batch.sort()

        self.assertEqual(actual_batch.batch_size, 5)
        # non-trivial test case
        res = actual_batch.frames
        for idx in res.index:
            self.assertTrue('car' in res['labels'][idx])

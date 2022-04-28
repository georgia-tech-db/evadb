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

from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all
from test.util import create_sample_video, file_remove, \
    copy_sample_video_to_prefix, load_inbuilt_udfs
from test.util import DummyObjectDetector

NUM_FRAMES = 10


class MaterializedViewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        create_sample_video()
        copy_sample_video_to_prefix()
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(load_query)
        query = """LOAD DATA INFILE 'ua_detrac.mp4'
                   INTO UATRAC;"""
        execute_query_fetch_all(query)
        load_inbuilt_udfs()

    @classmethod
    def tearDownClass(cls):
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
        expected = [{'dummy_view.id': i, 'dummy_view.label': labels[1 + i % 2]}
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
        expected = [{'dummy_view2.id': i,
                     'dummy_view2.label': labels[1 + i % 2]} for i in range(5)]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

    def test_should_mat_view_with_fastrcnn(self):
        select_query = """SELECT id, FastRCNNObjectDetector(data).labels
                            FROM UATRAC WHERE id < 5;"""
        query = '''CREATE MATERIALIZED VIEW IF NOT EXISTS uadtrac_fastRCNN (id, labels) \
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

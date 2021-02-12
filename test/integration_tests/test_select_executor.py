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
import os
import unittest

import numpy as np
import pandas as pd

from src.catalog.catalog_manager import CatalogManager
from src.models.storage.batch import Batch
from src.readers.opencv_reader import OpenCVReader
from test.util import create_sample_video, create_dummy_batches, perform_query

NUM_FRAMES = 10


class SelectExecutorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        perform_query(load_query)

    @classmethod
    def tearDownClass(cls):
        os.remove('dummy.avi')

    def test_sort_on_nonprojected_column(self):
        """ This tests doing an order by on a column
        that is not projected. The orderby_executor currently
        catches the KeyError, passes, and returns the untouched
        data
        """
        select_query = "SELECT data FROM MyVideo ORDER BY id;"
        actual_batch = perform_query(select_query)

        select_query = "SELECT data FROM MyVideo"
        expected_batch = perform_query(select_query)

        self.assertEqual(actual_batch, expected_batch)

    def test_should_load_and_sort_in_table(self):
        select_query = "SELECT data, id FROM MyVideo ORDER BY id;"
        actual_batch = perform_query(select_query)
        expected_rows = [{'id': i,
                          'data': np.array(np.ones((2, 2, 3)) *
                                           float(i + 1) * 25, dtype=np.uint8)
                          } for i in range(NUM_FRAMES)]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT data, id FROM MyVideo ORDER BY id DESC;"
        actual_batch = perform_query(select_query)
        expected_batch.reverse()
        self.assertEqual(actual_batch, expected_batch)

    def test_should_load_and_select_in_table(self):
        select_query = "SELECT id FROM MyVideo;"
        actual_batch = perform_query(select_query)
        actual_batch.sort()
        expected_rows = [{"id": i} for i in range(NUM_FRAMES)]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT id,data FROM MyVideo;"
        actual_batch = perform_query(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())
        self.assertEqual([actual_batch], expected_batch)

    @unittest.skip('Too slow when batch size is small.')
    def test_should_load_and_select_real_video_in_table(self):
        query = """LOAD DATA INFILE 'data/ua_detrac/ua_detrac.mp4'
                   INTO MyVideo;"""
        perform_query(query)

        select_query = "SELECT id,data FROM MyVideo;"
        actual_batch = perform_query(select_query)
        actual_batch.sort()
        video_reader = OpenCVReader('data/ua_detrac/ua_detrac/mp4')
        expected_batch = Batch(frames=pd.DataFrame())
        for batch in video_reader.read():
            expected_batch += batch
        self.assertTrue(actual_batch, expected_batch)

    def test_select_and_where_video_in_table(self):
        select_query = "SELECT id,data FROM MyVideo WHERE id = 5;"
        actual_batch = perform_query(select_query)
        expected_batch = list(create_dummy_batches(filters=[5]))[0]
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT data FROM MyVideo WHERE id = 5;"
        actual_batch = perform_query(select_query)
        expected_rows = [{"data": np.array(
            np.ones((2, 2, 3)) * float(5 + 1) * 25, dtype=np.uint8)}]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT id, data FROM MyVideo WHERE id >= 2;"
        actual_batch = perform_query(select_query)
        actual_batch.sort()
        expected_batch = list(
            create_dummy_batches(
                filters=range(
                    2, NUM_FRAMES)))[0]
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT id, data FROM MyVideo WHERE id >= 2 AND id < 5;"
        actual_batch = perform_query(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(filters=range(2, 5)))[0]

        self.assertEqual(actual_batch, expected_batch)

        nested_select_query = """SELECT id, data FROM
            (SELECT id, data FROM MyVideo WHERE id >= 2 AND id < 5)
            WHERE id >= 3;"""
        actual_batch = perform_query(nested_select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(filters=range(3, 5)))[0]
        self.assertEqual(actual_batch, expected_batch)

    def test_select_and_union_video_in_table(self):
        select_query = """SELECT id, data FROM MyVideo WHERE id < 3
            UNION ALL SELECT id, data FROM MyVideo WHERE id > 7;"""
        actual_batch = perform_query(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(
            filters=[i for i in range(NUM_FRAMES) if i < 3 or i > 7]))[0]
        self.assertEqual(actual_batch, expected_batch)

        select_query = """SELECT id, data FROM MyVideo WHERE id < 2
            UNION ALL SELECT id, data FROM MyVideo WHERE id > 4 AND id < 6
            UNION ALL SELECT id, data FROM MyVideo WHERE id > 7;"""
        actual_batch = perform_query(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(
            filters=[i for i in range(NUM_FRAMES)
                     if i < 2 or i == 5 or i > 7]))[0]
        self.assertEqual(actual_batch, expected_batch)

    def test_select_and_limit(self):
        select_query = "SELECT id,data FROM MyVideo LIMIT 5;"
        actual_batch = perform_query(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(
            num_frames=10, batch_size=5))

        self.assertEqual(actual_batch.batch_size, expected_batch[0].batch_size)
        self.assertEqual(actual_batch, expected_batch[0])

    def test_select_and_sample(self):
        select_query = "SELECT id,data FROM MyVideo SAMPLE 5;"
        actual_batch = perform_query(select_query)
        actual_batch.sort()

        expected_batch = list(create_dummy_batches(
            filters=range(0, NUM_FRAMES, 5)))

        self.assertEqual(actual_batch.batch_size, expected_batch[0].batch_size)
        self.assertEqual(actual_batch, expected_batch[0])

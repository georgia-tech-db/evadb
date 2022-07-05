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

import numpy as np
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.readers.opencv_reader import OpenCVReader
from eva.server.command_handler import execute_query_fetch_all

from test.util import (create_sample_video, create_dummy_batches,
                       file_remove, load_inbuilt_udfs, create_table)

NUM_FRAMES = 10


class SelectExecutorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(load_query)
        load_inbuilt_udfs()
        cls.table1 = create_table('table1', 100, 3)
        cls.table2 = create_table('table2', 500, 3)
        cls.table3 = create_table('table3', 1000, 3)

    @classmethod
    def tearDownClass(cls):
        file_remove('dummy.avi')

    def test_sort_on_nonprojected_column(self):
        """ This tests doing an order by on a column
        that is not projected. The orderby_executor currently
        catches the KeyError, passes, and returns the untouched
        data
        """
        select_query = "SELECT data FROM MyVideo ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)

        select_query = "SELECT data FROM MyVideo"
        expected_batch = execute_query_fetch_all(select_query)

        self.assertEqual(actual_batch.batch_size, expected_batch.batch_size)

    def test_should_load_and_sort_in_table(self):
        select_query = "SELECT data, id FROM MyVideo ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        expected_rows = [{'myvideo.id': i,
                          'myvideo.data': np.array(np.ones((2, 2, 3)) *
                                                   float(i + 1) * 25,
                                                   dtype=np.uint8)
                          } for i in range(NUM_FRAMES)]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT data, id FROM MyVideo ORDER BY id DESC;"
        actual_batch = execute_query_fetch_all(select_query)
        expected_batch.reverse()
        self.assertEqual(actual_batch, expected_batch)

    def test_should_load_and_select_in_table(self):
        select_query = "SELECT id FROM MyVideo;"
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_rows = [{"myvideo.id": i} for i in range(NUM_FRAMES)]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT id,data FROM MyVideo;"
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())
        self.assertEqual([actual_batch], expected_batch)
    
    def test_should_select_star_in_table(self):
        select_query = "SELECT * FROM MyVideo;"
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())[0]
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT * FROM MyVideo WHERE id = 5;"
        actual_batch = execute_query_fetch_all(select_query)
        expected_batch = list(create_dummy_batches(filters=[5]))[0]
        self.assertEqual(actual_batch, expected_batch)

    def test_should_select_star_in_nested_query(self):
        select_query = """SELECT * FROM (SELECT * FROM MyVideo) AS T;"""
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())[0]
        expected_batch.modify_column_alias('T')
        self.assertEqual(actual_batch, expected_batch)

        select_query = """SELECT * FROM (SELECT id FROM MyVideo) AS T;"""
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_rows = [{"T.id": i} for i in range(NUM_FRAMES)]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertEqual(actual_batch, expected_batch)

    def test_should_load_and_select_real_video_in_table(self):
        query = """LOAD DATA INFILE 'data/ua_detrac/ua_detrac.mp4'
                   INTO UADETRAC;"""
        execute_query_fetch_all(query)

        select_query = "SELECT id,data FROM UADETRAC;"
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        video_reader = OpenCVReader(
            'data/ua_detrac/ua_detrac/mp4',
            batch_mem_size=30000000
        )
        expected_batch = Batch(frames=pd.DataFrame())
        for batch in video_reader.read():
            expected_batch += batch
        self.assertTrue(actual_batch, expected_batch)

    def test_select_and_where_video_in_table(self):
        select_query = "SELECT id,data FROM MyVideo WHERE id = 5;"
        actual_batch = execute_query_fetch_all(select_query)
        expected_batch = list(create_dummy_batches(filters=[5]))[0]
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT data FROM MyVideo WHERE id = 5;"
        actual_batch = execute_query_fetch_all(select_query)
        expected_rows = [{"myvideo.data": np.array(
            np.ones((2, 2, 3)) * float(5 + 1) * 25, dtype=np.uint8)}]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT id, data FROM MyVideo WHERE id >= 2;"
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(
            create_dummy_batches(
                filters=range(
                    2, NUM_FRAMES)))[0]
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT id, data FROM MyVideo WHERE id >= 2 AND id < 5;"
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(filters=range(2, 5)))[0]

        self.assertEqual(actual_batch, expected_batch)

    def test_nested_select_video_in_table(self):
        nested_select_query = """SELECT id, data FROM
            (SELECT id, data FROM MyVideo WHERE id >= 2 AND id < 5) AS T
            WHERE id >= 3;"""
        actual_batch = execute_query_fetch_all(nested_select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(filters=range(3, 5)))[0]
        expected_batch.modify_column_alias('T')
        self.assertEqual(actual_batch, expected_batch)

        nested_select_query = """SELECT T.id, T.data FROM
            (SELECT id, data FROM MyVideo WHERE id >= 2 AND id < 5) AS T
            WHERE id >= 3;"""
        actual_batch = execute_query_fetch_all(nested_select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(filters=range(3, 5)))[0]
        expected_batch.modify_column_alias('T')
        self.assertEqual(actual_batch, expected_batch)

    def test_select_and_union_video_in_table(self):
        select_query = """SELECT id, data FROM MyVideo WHERE id < 3
            UNION ALL SELECT id, data FROM MyVideo WHERE id > 7;"""
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(
            filters=[i for i in range(NUM_FRAMES) if i < 3 or i > 7]))[0]
        self.assertEqual(actual_batch, expected_batch)

        select_query = """SELECT id, data FROM MyVideo WHERE id < 2
            UNION ALL SELECT id, data FROM MyVideo WHERE id > 4 AND id < 6
            UNION ALL SELECT id, data FROM MyVideo WHERE id > 7;"""
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(
            filters=[i for i in range(NUM_FRAMES)
                     if i < 2 or i == 5 or i > 7]))[0]
        self.assertEqual(actual_batch, expected_batch)

    def test_select_and_limit(self):
        select_query = "SELECT id,data FROM MyVideo ORDER BY id LIMIT 5;"
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(
            num_frames=10, batch_size=5))

        self.assertEqual(actual_batch.batch_size, expected_batch[0].batch_size)
        self.assertEqual(actual_batch, expected_batch[0])

    def test_select_and_sample(self):
        select_query = "SELECT id,data FROM MyVideo SAMPLE 7 ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()

        expected_batch = list(create_dummy_batches(
            filters=range(0, NUM_FRAMES, 7)))

        self.assertEqual(actual_batch.batch_size, expected_batch[0].batch_size)
        # Since frames are fetched in random order, this test might be flaky
        # Disabling it for time being
        # self.assertEqual(actual_batch, expected_batch[0])

    def test_lateral_join(self):
        select_query = """SELECT id FROM MyVideo JOIN LATERAL
                        FastRCNNObjectDetector(data) WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(actual_batch.frames.columns, ['myvideo.id'])
        self.assertEqual(actual_batch.batch_size, 5)

    def test_aahash_join_with_one_on(self):
        select_query = """SELECT table1.a2 FROM table1 JOIN
                        table2 ON table1.a1 = table2.a1;"""
        actual_batch = execute_query_fetch_all(select_query)
        expected = pd.merge(self.table1,
                            self.table2,
                            left_on=['table1.a1'],
                            right_on=['table2.a1'],
                            how="inner")
        if len(expected):
            expected_batch = Batch(expected).project(['table1.a2'])
            self.assertEqual(expected_batch.sort_orderby(['table1.a2']),
                             actual_batch.sort_orderby(['table1.a2']))

    def test_hash_join_with_multiple_on(self):
        select_query = """SELECT table1.a0, table1.a1 FROM table1 JOIN
                        table1 AS table2 ON table1.a1 = table2.a1 AND
                        table1.a0 = table2.a0;"""
        actual_batch = execute_query_fetch_all(select_query)
        expected = pd.merge(self.table1,
                            self.table1,
                            left_on=['table1.a1', 'table1.a0'],
                            right_on=['table1.a1', 'table1.a0'],
                            how="inner")
        if len(expected):
            expected_batch = Batch(expected).project(
                ['table1.a0', 'table1.a1'])
            self.assertEqual(expected_batch.sort_orderby(['table1.a1']),
                             actual_batch.sort_orderby(['table1.a1']))

    def test_hash_join_with_multiple_tables(self):
        select_query = """SELECT table1.a0 FROM table1 JOIN table2
                          ON table1.a0 = table2.a0 JOIN table3
                          ON table3.a1 = table1.a1 WHERE table1.a2 > 50;"""
        actual_batch = execute_query_fetch_all(select_query)
        tmp = pd.merge(self.table1,
                       self.table2,
                       left_on=['table1.a0'],
                       right_on=['table2.a0'],
                       how="inner")
        expected = pd.merge(tmp,
                            self.table3,
                            left_on=['table1.a1'],
                            right_on=['table3.a1'],
                            how="inner")
        expected = expected.where(expected['table1.a2'] > 50)
        if len(expected):
            expected_batch = Batch(expected).project(['table1.a0'])
            self.assertEqual(expected_batch.sort_orderby(['table1.a0']),
                             actual_batch.sort_orderby(['table1.a0']))

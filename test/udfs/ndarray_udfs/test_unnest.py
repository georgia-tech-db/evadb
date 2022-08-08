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
from test.util import NUM_FRAMES, create_sample_video, file_remove, load_inbuilt_udfs

import numpy as np
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all


class UnnestTests(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(load_query)
        load_inbuilt_udfs()

    def tearDown(self):
        file_remove("dummy.avi")

    # @unittest.skip('Unnest disabled')
    # def test_should_unnest_dataframe(self):
    #     query = """SELECT id, DummyMultiObjectDetector(data).labels
    #                FROM MyVideo ORDER BY id;"""
    #     without_unnest_batch = execute_query_fetch_all(query)
    #     query = """SELECT id, Unnest(DummyMultiObjectDetector(data).labels) \
    #                 FROM MyVideo ORDER BY id"""
    #     unnest_batch = execute_query_fetch_all(query)
    #     expected = Batch(Unnest().exec(without_unnest_batch.frames))
    #     expected.reset_index()
    #     self.assertEqual(unnest_batch, expected)

    # @unittest.skip('Unnest disabled')
    def test_should_unnest_dataframe_manual(self):
        query = """SELECT id, labels
                  FROM MyVideo JOIN LATERAL 
                    UNNEST(DummyMultiObjectDetector(data).labels)
                  WHERE id < 2 ORDER BY id;"""
        unnest_batch = execute_query_fetch_all(query)
        expected = Batch(
            pd.DataFrame(
                {
                    "myvideo.id": np.array([0, 0, 1, 1]),
                    "dummymultiobjectdetector.labels": np.array(
                        ["person", "person", "bicycle", "bicycle"]
                    ),
                }
            )
        )

        self.assertEqual(unnest_batch, expected)

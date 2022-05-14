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
# import unittest
# import pandas as pd
# import numpy as np
# from pytest import skip

# from eva.catalog.catalog_manager import CatalogManager
# from eva.models.storage.batch import Batch
# from eva.server.command_handler import execute_query_fetch_all
# # from eva.udfs.ndarray_udfs.unnest import Unnest
# from test.util import create_sample_video, load_inbuilt_udfs, file_remove
# from test.util import NUM_FRAMES


# class UnnestTests(unittest.TestCase):

#     def setUp(self):
#         CatalogManager().reset()
#         create_sample_video(NUM_FRAMES)
#         load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
#         execute_query_fetch_all(load_query)
#         load_inbuilt_udfs()

#     def tearDown(self):
#         file_remove('dummy.avi')

#     @unittest.skip('Unnest disabled')
#     def test_should_unnest_dataframe(self):
#         query = """SELECT id, DummyMultiObjectDetector(data).labels
#                    FROM MyVideo ORDER BY id;"""
#         without_unnest_batch = execute_query_fetch_all(query)
#         query = """SELECT id, Unnest(DummyMultiObjectDetector(data).labels) \
#                     FROM MyVideo ORDER BY id"""
#         unnest_batch = execute_query_fetch_all(query)
#         expected = Batch(Unnest().exec(without_unnest_batch.frames))
#         expected.reset_index()
#         self.assertEqual(unnest_batch, expected)

#     @unittest.skip('Unnest disabled')
#     def test_should_unnest_dataframe_manual(self):
#         query = """SELECT id, Unnest(DummyMultiObjectDetector(data).labels)
#                   FROM MyVideo WHERE id < 2 ORDER BY id;"""
#         unnest_batch = execute_query_fetch_all(query)
#         expected = Batch(pd.DataFrame(
#             {'myvideo.id': np.array([0, 0, 1, 1]),
#              'unnest.out': np.array(['person','person','
#                                       bicycle',bicycle'])}))

#         self.assertEqual(unnest_batch, expected)

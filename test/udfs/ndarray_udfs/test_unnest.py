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
from src.udfs.ndarray_udfs.unnest import Unnest


class UnnestTests(unittest.TestCase):

    def setUp(self):
        return
        CatalogManager().reset()
        load_query = """LOAD DATA INFILE 'data/ua_detrac/ua_detrac.mp4'
                        INTO MyVideo;"""
        execute_query_fetch_all(load_query)

    def test_should_unnest_dataframe(self):
        query = """SELECT FastRCNNObjectDetector(data).labels FROM
                    MyVideo WHERE id < 2;"""
        without_unnest_batch = execute_query_fetch_all(query)
        query = """SELECT Unnest(FastRCNNObjectDetector(data).labels) FROM
                    MyVideo WHERE id < 2;"""
        unnest_batch = execute_query_fetch_all(query)
        expected = Batch(Unnest().exec(without_unnest_batch.frames))
        expected.reset_index()
        self.assertEqual(unnest_batch, expected)

    def test_should_unnest_dataframe_manual(self):
        query = """SELECT Unnest(FastRCNNObjectDetector(data).labels) FROM
                    MyVideo WHERE id < 2 LIMIT 2;"""
        unnest_batch = execute_query_fetch_all(query)
        expected = Batch(pd.DataFrame({'labels': ['person', 'car']}))
        self.assertEqual(unnest_batch, expected)

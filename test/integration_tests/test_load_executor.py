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
from src.storage import StorageEngine

from test.util import create_sample_video, create_dummy_batches, perform_query


class LoadExecutorTest(unittest.TestCase):

    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        create_sample_video()

    def tearDown(self):
        os.remove('dummy.avi')

    # integration test
    def test_should_load_video_in_table(self):
        query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""

        perform_query(query)

        metadata = CatalogManager().get_dataset_metadata("", "MyVideo")
        actual_batch = Batch(pd.DataFrame())
        for batch in StorageEngine.read(metadata):
            actual_batch += batch
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())
        self.assertEqual([actual_batch], expected_batch)

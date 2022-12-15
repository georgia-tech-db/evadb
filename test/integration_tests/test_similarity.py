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
import os
import unittest
from test.util import create_sample_image, load_inbuilt_udfs

import numpy as np
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all
from eva.storage.storage_engine import StorageEngine


class SimilarityTests(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()

        # Prepare needed UDFs and data.
        load_inbuilt_udfs()
        create_sample_image()

        # Create base comparison table.
        create_table_query = "CREATE TABLE IF NOT EXISTS testSimilarityTable (data NDARRAY UINT8(3, ANYDIM, ANYDIM));"
        execute_query_fetch_all(create_table_query)

        # Prepare injected data.
        base_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        base_img[0] -= 1
        base_img[2] += 1

        # id: 1 -> most dissimilar, id: 5 -> most similar
        base_img += 4

        # Inject data.
        table_df_metadata = CatalogManager().get_dataset_metadata(
            None, "testSimilarityTable"
        )
        storage_engine = StorageEngine.factory(table_df_metadata)
        for _ in range(5):
            storage_engine.write(
                table_df_metadata, Batch(pd.DataFrame([{"data": base_img}]))
            )
            base_img -= 1

    def tearDown(self):
        drop_table_query = "DROP TABLE testSimilarityTable;"
        execute_query_fetch_all(drop_table_query)

    def test_similarity_should_work_in_order(self):
        config = ConfigurationManager()
        upload_dir_from_config = config.get_value("storage", "upload_dir")
        img_path = os.path.join(upload_dir_from_config, "dummy.jpg")

        # Top 1.
        select_query = """SELECT data FROM testSimilarityTable ORDER BY Similarity(Open("{}"), data, "DummyFeatureExtractor") LIMIT 1;""".format(
            img_path
        )
        actual_batch = execute_query_fetch_all(select_query)

        base_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        base_img[0] -= 1
        base_img[2] += 1

        actual_open = actual_batch.frames["testsimilaritytable.data"].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img))
        actual_distance = actual_batch.frames["similarity.distance"].to_numpy()[0]
        self.assertEqual(actual_distance, 0)

        # Top 2.
        select_query = """SELECT data FROM testSimilarityTable ORDER BY Similarity(Open("{}"), data, "DummyFeatureExtractor") LIMIT 2;""".format(
            img_path
        )
        actual_batch = execute_query_fetch_all(select_query)

        base_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        base_img[0] -= 1
        base_img[2] += 1

        actual_open = actual_batch.frames["testsimilaritytable.data"].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img))
        actual_open = actual_batch.frames["testsimilaritytable.data"].to_numpy()[1]
        self.assertTrue(np.array_equal(actual_open, base_img + 1))
        actual_distance = actual_batch.frames["similarity.distance"].to_numpy()[0]
        self.assertEqual(actual_distance, 0)
        actual_distance = actual_batch.frames["similarity.distance"].to_numpy()[1]
        self.assertEqual(actual_distance, 27)

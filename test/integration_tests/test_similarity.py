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

        # Prepare needed UDFs and data_col.
        load_inbuilt_udfs()
        create_sample_image()

        # Create base comparison table.
        create_table_query = """CREATE TABLE IF NOT EXISTS testSimilarityTable
                                  (data_col NDARRAY UINT8(3, ANYDIM, ANYDIM),
                                   dummy INTEGER);"""
        execute_query_fetch_all(create_table_query)

        # Create feature table.
        create_table_query = """CREATE TABLE IF NOT EXISTS testSimilarityFeatureTable
                                  (feature_col NDARRAY FLOAT32(1, ANYDIM),
                                   dummy INTEGER);"""
        execute_query_fetch_all(create_table_query)

        # Prepare injected data_col.
        base_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        base_img[0] -= 1
        base_img[2] += 1

        # id: 1 -> most dissimilar, id: 5 -> most similar
        base_img += 4

        # Inject data_col.
        base_table_catalog_entry = CatalogManager().get_table_catalog_entry(
            "testSimilarityTable"
        )
        feature_table_catalog_entry = CatalogManager().get_table_catalog_entry(
            "testSimilarityFeatureTable"
        )
        storage_engine = StorageEngine.factory(base_table_catalog_entry)
        for i in range(5):
            storage_engine.write(
                base_table_catalog_entry,
                Batch(
                    pd.DataFrame(
                        [
                            {
                                "data_col": base_img,
                                "dummy": i,
                            }
                        ]
                    )
                ),
            )
            storage_engine.write(
                feature_table_catalog_entry,
                Batch(
                    pd.DataFrame(
                        [
                            {
                                "feature_col": base_img.astype(np.float32).reshape(
                                    1, -1
                                ),
                                "dummy": i,
                            }
                        ]
                    )
                ),
            )
            base_img -= 1

    def tearDown(self):
        drop_table_query = "DROP TABLE testSimilarityTable;"
        execute_query_fetch_all(drop_table_query)
        drop_table_query = "DROP TABLE testSimilarityFeatureTable;"
        execute_query_fetch_all(drop_table_query)

    def test_similarity_should_work_in_order(self):
        config = ConfigurationManager()
        upload_dir_from_config = config.get_value("storage", "upload_dir")
        img_path = os.path.join(upload_dir_from_config, "dummy.jpg")

        ###############################################
        # Test case runs with UDF on raw input table. #
        ###############################################

        # Top 1 - assume table contains base data_col.
        select_query = """SELECT data_col FROM testSimilarityTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                            LIMIT 1;""".format(
            img_path
        )
        actual_batch = execute_query_fetch_all(select_query)

        base_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        base_img[0] -= 1
        base_img[2] += 1

        actual_open = actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img))
        # actual_distance = actual_batch.frames["similarity.distance"].to_numpy()[0]
        # self.assertEqual(actual_distance, 0)

        # Top 2 - assume table contains base data.
        select_query = """SELECT data_col FROM testSimilarityTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                            LIMIT 2;""".format(
            img_path
        )
        actual_batch = execute_query_fetch_all(select_query)

        actual_open = actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img))
        actual_open = actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[1]
        self.assertTrue(np.array_equal(actual_open, base_img + 1))
        # actual_distance = actual_batch.frames["similarity.distance"].to_numpy()[0]
        # self.assertEqual(actual_distance, 0)
        # actual_distance = actual_batch.frames["similarity.distance"].to_numpy()[1]
        # self.assertEqual(actual_distance, 27)

        ###########################################
        # Test case runs on feature vector table. #
        ###########################################

        # Top 1 - assume table contains feature data.
        select_query = """SELECT feature_col FROM testSimilarityFeatureTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), feature_col)
                            LIMIT 1;""".format(
            img_path
        )
        actual_batch = execute_query_fetch_all(select_query)

        base_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        base_img[0] -= 1
        base_img[2] += 1
        base_img = base_img.astype(np.float32).reshape(1, -1)

        actual_open = actual_batch.frames[
            "testsimilarityfeaturetable.feature_col"
        ].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img))
        # actual_distance = actual_batch.frames["similarity.distance"].to_numpy()[0]
        # self.assertEqual(actual_distance, 0)

        # Top 2 - assume table contains feature data.
        select_query = """SELECT feature_col FROM testSimilarityFeatureTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), feature_col)
                            LIMIT 2;""".format(
            img_path
        )
        actual_batch = execute_query_fetch_all(select_query)

        actual_open = actual_batch.frames[
            "testsimilarityfeaturetable.feature_col"
        ].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img))
        actual_open = actual_batch.frames[
            "testsimilarityfeaturetable.feature_col"
        ].to_numpy()[1]
        self.assertTrue(np.array_equal(actual_open, base_img + 1))
        # actual_distance = actual_batch.frames["similarity.distance"].to_numpy()[0]
        # self.assertEqual(actual_distance, 0)
        # actual_distance = actual_batch.frames["similarity.distance"].to_numpy()[1]
        # self.assertEqual(actual_distance, 27)

    def test_should_do_faiss_index_scan(self):
        config = ConfigurationManager()
        upload_dir_from_config = config.get_value("storage", "upload_dir")
        img_path = os.path.join(upload_dir_from_config, "dummy.jpg")

        ###########################################
        # Test case runs on feature vector table. #
        ###########################################

        # Execution without index scan.
        select_query = """SELECT feature_col FROM testSimilarityFeatureTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), feature_col)
                            LIMIT 3;""".format(
            img_path
        )
        expected_batch = execute_query_fetch_all(select_query)

        # Execution with index scan.
        create_index_query = """CREATE INDEX testFaissIndexScanRewrite1
                                    ON testSimilarityFeatureTable (feature_col)
                                    USING HNSW;"""
        execute_query_fetch_all(create_index_query)
        select_query = """SELECT feature_col FROM testSimilarityFeatureTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), feature_col)
                            LIMIT 3;""".format(
            img_path
        )
        explain_query = """EXPLAIN {}""".format(select_query)
        explain_batch = execute_query_fetch_all(explain_query)
        self.assertTrue("FaissIndexScan" in explain_batch.frames[0][0])
        actual_batch = execute_query_fetch_all(select_query)

        self.assertEqual(len(actual_batch), 3)
        for i in range(3):
            self.assertTrue(
                np.array_equal(
                    expected_batch.frames[
                        "testsimilarityfeaturetable.feature_col"
                    ].to_numpy()[i],
                    actual_batch.frames[
                        "testsimilarityfeaturetable.feature_col"
                    ].to_numpy()[i],
                )
            )

        ###############################################
        # Test case runs with UDF on raw input table. #
        ###############################################

        # Execution without index scan.
        select_query = """SELECT data_col FROM testSimilarityTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                            LIMIT 3;""".format(
            img_path
        )
        expected_batch = execute_query_fetch_all(select_query)

        # Execution with index scan.
        create_index_query = """CREATE INDEX testFaissIndexScanRewrite2
                                    ON testSimilarityTable (DummyFeatureExtractor(data_col))
                                    USING HNSW;"""
        execute_query_fetch_all(create_index_query)
        select_query = """SELECT data_col FROM testSimilarityTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                            LIMIT 3;""".format(
            img_path
        )
        explain_query = """EXPLAIN {}""".format(select_query)
        explain_batch = execute_query_fetch_all(explain_query)
        self.assertTrue("FaissIndexScan" in explain_batch.frames[0][0])
        actual_batch = execute_query_fetch_all(select_query)

        self.assertEqual(len(actual_batch), 3)
        for i in range(3):
            self.assertTrue(
                np.array_equal(
                    expected_batch.frames["testsimilaritytable.data_col"].to_numpy()[i],
                    actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[i],
                )
            )

        # Cleanup
        CatalogManager().drop_index_catalog_entry("testFaissIndexScanRewrite1")
        CatalogManager().drop_index_catalog_entry("testFaissIndexScanRewrite2")

    def test_should_not_do_faiss_index_scan_with_predicate(self):
        # Execution with index scan.
        create_index_query = """CREATE INDEX testFaissIndexScanRewrite
                                    ON testSimilarityTable (DummyFeatureExtractor(data_col))
                                    USING HNSW;"""
        execute_query_fetch_all(create_index_query)

        explain_query = """
            EXPLAIN
                SELECT data_col FROM testSimilarityTable WHERE dummy = 0
                  ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                  LIMIT 3;
        """.format(
            "dummypath"
        )
        batch = execute_query_fetch_all(explain_query)

        # Index scan should not be used.
        self.assertFalse("FaissIndexScan" in batch.frames[0][0])

        # Cleanup
        CatalogManager().drop_index_catalog_entry("testFaissIndexScanRewrite")

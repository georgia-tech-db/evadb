# coding=utf-8
# Copyright 2018-2023 EvaDB
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
import time
import unittest
from test.markers import chromadb_skip_marker, pinecone_skip_marker, qdrant_skip_marker
from test.util import (
    create_sample_image,
    get_evadb_for_testing,
    load_functions_for_testing,
    shutdown_ray,
)

import numpy as np
import pandas as pd
import pytest

from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all
from evadb.storage.storage_engine import StorageEngine
from evadb.utils.generic_utils import try_to_import_cv2


@pytest.mark.notparallel
class SimilarityTests(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()

        # Prepare needed Functions and data_col.
        load_functions_for_testing(self.evadb, mode="debug")
        self.img_path = create_sample_image()

        # Create base comparison table.
        create_table_query = """CREATE TABLE IF NOT EXISTS testSimilarityTable
                                  (data_col NDARRAY UINT8(3, ANYDIM, ANYDIM),
                                   dummy INTEGER);"""
        execute_query_fetch_all(self.evadb, create_table_query)

        # Create feature table.
        create_table_query = """CREATE TABLE IF NOT EXISTS testSimilarityFeatureTable
                                  (feature_col NDARRAY FLOAT32(1, ANYDIM),
                                   dummy INTEGER);"""
        execute_query_fetch_all(self.evadb, create_table_query)

        # Prepare injected data_col.
        base_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        base_img[0] -= 1
        base_img[2] += 1

        # id: 1 -> most dissimilar, id: 5 -> most similar
        base_img += 4

        # Inject data_col.
        base_table_catalog_entry = self.evadb.catalog().get_table_catalog_entry(
            "testSimilarityTable"
        )
        feature_table_catalog_entry = self.evadb.catalog().get_table_catalog_entry(
            "testSimilarityFeatureTable"
        )

        # Image list.
        self.img_path_list = []

        storage_engine = StorageEngine.factory(self.evadb, base_table_catalog_entry)
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

            # Create an actual image dataset.
            img_save_path = os.path.join(
                self.evadb.config.get_value("storage", "tmp_dir"),
                f"test_similar_img{i}.jpg",
            )
            try_to_import_cv2()
            import cv2

            cv2.imwrite(img_save_path, base_img)
            load_image_query = (
                f"LOAD IMAGE '{img_save_path}' INTO testSimilarityImageDataset;"
            )
            execute_query_fetch_all(self.evadb, load_image_query)

            self.img_path_list.append(img_save_path)

            base_img -= 1

        # Set the env variables.
        self.original_pinecone_key = os.environ.get("PINECONE_API_KEY")
        self.original_pinecone_env = os.environ.get("PINECONE_ENV")

        os.environ["PINECONE_API_KEY"] = "657e4fae-7208-4555-b0f2-9847dfa5b818"
        os.environ["PINECONE_ENV"] = "gcp-starter"

    def tearDown(self):
        shutdown_ray()

        drop_table_query = "DROP TABLE testSimilarityTable;"
        execute_query_fetch_all(self.evadb, drop_table_query)
        drop_table_query = "DROP TABLE testSimilarityFeatureTable;"
        execute_query_fetch_all(self.evadb, drop_table_query)
        drop_table_query = "DROP TABLE IF EXISTS testSimilarityImageDataset;"
        execute_query_fetch_all(self.evadb, drop_table_query)
        # Reset the env variables.
        if self.original_pinecone_key:
            os.environ["PINECONE_API_KEY"] = self.original_pinecone_key
        else:
            del os.environ["PINECONE_API_KEY"]
        if self.original_pinecone_env:
            os.environ["PINECONE_ENV"] = self.original_pinecone_env
        else:
            del os.environ["PINECONE_ENV"]

    def test_similarity_should_work_in_order(self):
        ###############################################
        # Test case runs with Function on raw input table. #
        ###############################################

        # Top 1 - assume table contains base data_col.
        select_query = """SELECT data_col FROM testSimilarityTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                            LIMIT 1;""".format(
            self.img_path
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

        base_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        base_img[0] -= 1
        base_img[2] += 1

        actual_open = actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img))

        # Top 2 - assume table contains base data.
        select_query = """SELECT data_col FROM testSimilarityTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                            LIMIT 2;""".format(
            self.img_path
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

        actual_open = actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img))
        actual_open = actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[1]
        self.assertTrue(np.array_equal(actual_open, base_img + 1))

        # Top 2 - descending order
        select_query = """SELECT data_col FROM testSimilarityTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col)) DESC
                            LIMIT 2;""".format(
            self.img_path
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

        actual_open = actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img + 4))
        actual_open = actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[1]
        self.assertTrue(np.array_equal(actual_open, base_img + 3))

        ###########################################
        # Test case runs on feature vector table. #
        ###########################################

        # Top 1 - assume table contains feature data.
        select_query = """SELECT feature_col FROM testSimilarityFeatureTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), feature_col)
                            LIMIT 1;""".format(
            self.img_path
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

        base_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        base_img[0] -= 1
        base_img[2] += 1
        base_img = base_img.astype(np.float32).reshape(1, -1)

        actual_open = actual_batch.frames[
            "testsimilarityfeaturetable.feature_col"
        ].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img))

        # Top 2 - assume table contains feature data.
        select_query = """SELECT feature_col FROM testSimilarityFeatureTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), feature_col)
                            LIMIT 2;""".format(
            self.img_path
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

        actual_open = actual_batch.frames[
            "testsimilarityfeaturetable.feature_col"
        ].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img))
        actual_open = actual_batch.frames[
            "testsimilarityfeaturetable.feature_col"
        ].to_numpy()[1]
        self.assertTrue(np.array_equal(actual_open, base_img + 1))

    def test_should_do_vector_index_scan(self):
        ###########################################
        # Test case runs on feature vector table. #
        ###########################################

        # Execution without index scan.
        select_query = """SELECT feature_col FROM testSimilarityFeatureTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), feature_col)
                            LIMIT 3;""".format(
            self.img_path
        )
        expected_batch = execute_query_fetch_all(self.evadb, select_query)

        # Execution with index scan.
        create_index_query = """CREATE INDEX testFaissIndexScanRewrite1
                                    ON testSimilarityFeatureTable (feature_col)
                                    USING FAISS;"""
        execute_query_fetch_all(self.evadb, create_index_query)
        select_query = """SELECT feature_col FROM testSimilarityFeatureTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), feature_col)
                            LIMIT 3;""".format(
            self.img_path
        )
        explain_query = """EXPLAIN {}""".format(select_query)
        explain_batch = execute_query_fetch_all(self.evadb, explain_query)
        self.assertTrue("VectorIndexScan" in explain_batch.frames[0][0])
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

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
        # Test case runs with Function on raw input table. #
        ###############################################

        # Execution without index scan.
        select_query = """SELECT data_col FROM testSimilarityTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                            LIMIT 3;""".format(
            self.img_path
        )
        expected_batch = execute_query_fetch_all(self.evadb, select_query)

        # Execution with index scan.
        create_index_query = """CREATE INDEX testFaissIndexScanRewrite2
                                    ON testSimilarityTable (DummyFeatureExtractor(data_col))
                                    USING FAISS;"""
        execute_query_fetch_all(self.evadb, create_index_query)
        select_query = """SELECT data_col FROM testSimilarityTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                            LIMIT 3;""".format(
            self.img_path
        )
        explain_query = """EXPLAIN {}""".format(select_query)
        explain_batch = execute_query_fetch_all(self.evadb, explain_query)
        self.assertTrue("VectorIndexScan" in explain_batch.frames[0][0])
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

        self.assertEqual(len(actual_batch), 3)
        for i in range(3):
            self.assertTrue(
                np.array_equal(
                    expected_batch.frames["testsimilaritytable.data_col"].to_numpy()[i],
                    actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[i],
                )
            )

        # Cleanup
        drop_query = "DROP INDEX testFaissIndexScanRewrite1"
        execute_query_fetch_all(self.evadb, drop_query)
        drop_query = "DROP INDEX testFaissIndexScanRewrite2"
        execute_query_fetch_all(self.evadb, drop_query)

    def test_should_not_do_vector_index_scan_with_desc_order(self):
        # Execution with index scan.
        create_index_query = """CREATE INDEX testFaissIndexScanRewrite
                                    ON testSimilarityTable (DummyFeatureExtractor(data_col))
                                    USING FAISS;"""
        execute_query_fetch_all(self.evadb, create_index_query)

        explain_query = """
            EXPLAIN
                SELECT data_col FROM testSimilarityTable WHERE dummy = 0
                  ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                  LIMIT 3;
        """.format(
            "dummypath"
        )
        batch = execute_query_fetch_all(self.evadb, explain_query)

        # Index scan should not be used.
        self.assertFalse("FaissIndexScan" in batch.frames[0][0])

        # Check results are in descending order
        base_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        base_img[0] -= 1
        base_img[2] += 1

        select_query = """SELECT data_col FROM testSimilarityTable
                            ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col)) DESC
                            LIMIT 2;""".format(
            self.img_path
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

        actual_open = actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[0]
        self.assertTrue(np.array_equal(actual_open, base_img + 4))
        actual_open = actual_batch.frames["testsimilaritytable.data_col"].to_numpy()[1]
        self.assertTrue(np.array_equal(actual_open, base_img + 3))

        # Cleanup
        drop_query = "DROP INDEX testFaissIndexScanRewrite"
        execute_query_fetch_all(self.evadb, drop_query)

    def test_should_not_do_vector_index_scan_with_predicate(self):
        # Execution with index scan.
        create_index_query = """CREATE INDEX testFaissIndexScanRewrite
                                    ON testSimilarityTable (DummyFeatureExtractor(data_col))
                                    USING FAISS;"""
        execute_query_fetch_all(self.evadb, create_index_query)

        explain_query = """
            EXPLAIN
                SELECT data_col FROM testSimilarityTable WHERE dummy = 0
                  ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data_col))
                  LIMIT 3;
        """.format(
            "dummypath"
        )
        batch = execute_query_fetch_all(self.evadb, explain_query)

        # Index scan should not be used.
        self.assertFalse("FaissIndexScan" in batch.frames[0][0])

        # Cleanup
        drop_query = "DROP INDEX testFaissIndexScanRewrite"
        execute_query_fetch_all(self.evadb, drop_query)

    def test_end_to_end_index_scan_should_work_correctly_on_image_dataset_faiss(self):
        for _ in range(2):
            create_index_query = """CREATE INDEX testFaissIndexImageDataset
                                        ON testSimilarityImageDataset (DummyFeatureExtractor(data))
                                        USING FAISS;"""
            execute_query_fetch_all(self.evadb, create_index_query)

            select_query = """SELECT _row_id FROM testSimilarityImageDataset
                                ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data))
                                LIMIT 1;""".format(
                self.img_path
            )
            explain_batch = execute_query_fetch_all(
                self.evadb, f"EXPLAIN {select_query}"
            )
            self.assertTrue("VectorIndexScan" in explain_batch.frames[0][0])

            res_batch = execute_query_fetch_all(self.evadb, select_query)
            self.assertEqual(
                res_batch.frames["testsimilarityimagedataset._row_id"][0], 5
            )

            # Cleanup
            drop_query = "DROP INDEX testFaissIndexImageDataset"
            execute_query_fetch_all(self.evadb, drop_query)

    def test_index_auto_update_on_structured_table_during_insertion_with_faiss(self):
        create_query = "CREATE TABLE testIndexAutoUpdate (img_path TEXT(100))"
        execute_query_fetch_all(self.evadb, create_query)

        for i, img_path in enumerate(self.img_path_list):
            insert_query = (
                f"INSERT INTO testIndexAutoUpdate (img_path) VALUES ('{img_path}')"
            )
            execute_query_fetch_all(self.evadb, insert_query)
            if i == 0:
                create_index_query = "CREATE INDEX testIndex ON testIndexAutoUpdate(DummyFeatureExtractor(Open(img_path))) USING FAISS"
                execute_query_fetch_all(self.evadb, create_index_query)

        select_query = """SELECT _row_id FROM testIndexAutoUpdate
                                ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(Open(img_path)))
                                LIMIT 1;""".format(
            self.img_path
        )
        explain_batch = execute_query_fetch_all(self.evadb, f"EXPLAIN {select_query}")
        self.assertTrue("VectorIndexScan" in explain_batch.frames[0][0])

        res_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(res_batch.frames["testindexautoupdate._row_id"][0], 5)

    @qdrant_skip_marker
    def test_end_to_end_index_scan_should_work_correctly_on_image_dataset_qdrant(self):
        for _ in range(2):
            create_index_query = """CREATE INDEX testQdrantIndexImageDataset
                                        ON testSimilarityImageDataset (DummyFeatureExtractor(data))
                                        USING QDRANT;"""
            execute_query_fetch_all(self.evadb, create_index_query)

            select_query = """SELECT _row_id FROM testSimilarityImageDataset
                                ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data))
                                LIMIT 1;""".format(
                self.img_path
            )
            explain_batch = execute_query_fetch_all(
                self.evadb, f"EXPLAIN {select_query}"
            )
            self.assertTrue("VectorIndexScan" in explain_batch.frames[0][0])

            """|__ ProjectPlan
                |__ VectorIndexScanPlan
                    |__ SeqScanPlan
                        |__ StoragePlan"""

            res_batch = execute_query_fetch_all(self.evadb, select_query)
            self.assertEqual(
                res_batch.frames["testsimilarityimagedataset._row_id"][0], 5
            )

            # Cleanup
            drop_query = "DROP INDEX testQdrantIndexImageDataset"
            execute_query_fetch_all(self.evadb, drop_query)

    @chromadb_skip_marker
    def test_end_to_end_index_scan_should_work_correctly_on_image_dataset_chromadb(
        self,
    ):
        for _ in range(2):
            create_index_query = """CREATE INDEX testChromaDBIndexImageDataset
                                    ON testSimilarityImageDataset (DummyFeatureExtractor(data))
                                    USING CHROMADB;"""
            execute_query_fetch_all(self.evadb, create_index_query)

            select_query = """SELECT _row_id FROM testSimilarityImageDataset
                                ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data))
                                LIMIT 1;""".format(
                self.img_path
            )
            explain_batch = execute_query_fetch_all(
                self.evadb, f"EXPLAIN {select_query}"
            )
            self.assertTrue("VectorIndexScan" in explain_batch.frames[0][0])

            res_batch = execute_query_fetch_all(self.evadb, select_query)
            self.assertEqual(
                res_batch.frames["testsimilarityimagedataset._row_id"][0], 5
            )

            # Cleanup
            drop_query = "DROP INDEX testChromaDBIndexImageDataset"
            execute_query_fetch_all(self.evadb, drop_query)

    @pytest.mark.skip(reason="Flaky testcase due to `bad request` error message")
    @pinecone_skip_marker
    def test_end_to_end_index_scan_should_work_correctly_on_image_dataset_pinecone(
        self,
    ):
        for _ in range(2):
            create_index_query = """CREATE INDEX testpineconeindeximagedataset
                                    ON testSimilarityImageDataset (DummyFeatureExtractor(data))
                                    USING PINECONE;"""
            execute_query_fetch_all(self.evadb, create_index_query)
            # Sleep to ensure the pinecone records get updated as Pinecone is eventually consistent.
            time.sleep(20)

            select_query = """SELECT _row_id FROM testSimilarityImageDataset
                                ORDER BY Similarity(DummyFeatureExtractor(Open("{}")), DummyFeatureExtractor(data))
                                LIMIT 1;""".format(
                self.img_path
            )
            explain_batch = execute_query_fetch_all(
                self.evadb, f"EXPLAIN {select_query}"
            )
            self.assertTrue("VectorIndexScan" in explain_batch.frames[0][0])

            res_batch = execute_query_fetch_all(self.evadb, select_query)
            self.assertEqual(
                res_batch.frames["testsimilarityimagedataset._row_id"][0], 5
            )

            drop_index_query = "DROP INDEX testpineconeindeximagedataset;"
            execute_query_fetch_all(self.evadb, drop_index_query)

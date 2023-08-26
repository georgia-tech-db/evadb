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
import unittest
from pathlib import Path
from test.markers import macos_skip_marker
from test.util import get_evadb_for_testing, load_udfs_for_testing

import numpy as np
import pandas as pd
import pytest

from evadb.catalog.catalog_type import VectorStoreType
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all
from evadb.storage.storage_engine import StorageEngine
from evadb.utils.generic_utils import try_to_import_faiss


@pytest.mark.notparallel
class CreateIndexTest(unittest.TestCase):
    def _index_save_path(self):
        return str(
            Path(self.evadb.config.get_value("storage", "index_dir"))
            / Path("{}_{}.index".format("FAISS", "testCreateIndexName"))
        )

    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        load_udfs_for_testing(cls.evadb, mode="debug")

        # Create feature vector table and raw input table.
        feat1 = np.array([[0, 0, 0]]).astype(np.float32)
        feat2 = np.array([[100, 100, 100]]).astype(np.float32)
        feat3 = np.array([[200, 200, 200]]).astype(np.float32)

        input1 = np.array([[0, 0, 0]]).astype(np.uint8)
        input2 = np.array([[100, 100, 100]]).astype(np.uint8)
        input3 = np.array([[200, 200, 200]]).astype(np.uint8)

        # Create table.
        execute_query_fetch_all(
            cls.evadb,
            """create table if not exists testCreateIndexFeatTable (
                feat NDARRAY FLOAT32(1,3)
            );""",
        )
        execute_query_fetch_all(
            cls.evadb,
            """create table if not exists testCreateIndexInputTable (
                input NDARRAY UINT8(1,3)
            );""",
        )

        # Create pandas dataframe.
        feat_batch_data = Batch(
            pd.DataFrame(
                data={
                    "feat": [feat1, feat2, feat3],
                }
            )
        )
        feat_tb_entry = cls.evadb.catalog().get_table_catalog_entry(
            "testCreateIndexFeatTable"
        )
        storage_engine = StorageEngine.factory(cls.evadb, feat_tb_entry)
        storage_engine.write(feat_tb_entry, feat_batch_data)

        input_batch_data = Batch(
            pd.DataFrame(
                data={
                    "input": [input1, input2, input3],
                }
            )
        )
        input_tb_entry = cls.evadb.catalog().get_table_catalog_entry(
            "testCreateIndexInputTable"
        )
        storage_engine.write(input_tb_entry, input_batch_data)

    @classmethod
    def tearDownClass(cls):
        query = "DROP TABLE testCreateIndexFeatTable;"
        execute_query_fetch_all(cls.evadb, query)
        query = "DROP TABLE testCreateIndexInputTable;"
        execute_query_fetch_all(cls.evadb, query)

    @macos_skip_marker
    def test_should_create_index_faiss(self):
        query = "CREATE INDEX testCreateIndexName ON testCreateIndexFeatTable (feat) USING FAISS;"
        execute_query_fetch_all(self.evadb, query)

        # Test index catalog.
        index_catalog_entry = self.evadb.catalog().get_index_catalog_entry_by_name(
            "testCreateIndexName"
        )
        self.assertEqual(index_catalog_entry.type, VectorStoreType.FAISS)
        self.assertEqual(
            index_catalog_entry.save_file_path,
            self._index_save_path(),
        )
        self.assertEqual(
            index_catalog_entry.udf_signature,
            None,
        )

        # Test referenced column.
        feat_table_entry = self.evadb.catalog().get_table_catalog_entry(
            "testCreateIndexFeatTable"
        )
        feat_column = [col for col in feat_table_entry.columns if col.name == "feat"][0]
        self.assertEqual(index_catalog_entry.feat_column_id, feat_column.row_id)
        self.assertEqual(index_catalog_entry.feat_column, feat_column)

        # Test on disk index.
        try_to_import_faiss()
        import faiss

        index = faiss.read_index(index_catalog_entry.save_file_path)
        distance, row_id = index.search(np.array([[0, 0, 0]]).astype(np.float32), 1)
        self.assertEqual(distance[0][0], 0)
        self.assertEqual(row_id[0][0], 1)

        # Cleanup.
        self.evadb.catalog().drop_index_catalog_entry("testCreateIndexName")

    @macos_skip_marker
    def test_should_create_index_with_udf(self):
        query = "CREATE INDEX testCreateIndexName ON testCreateIndexInputTable (DummyFeatureExtractor(input)) USING FAISS;"
        execute_query_fetch_all(self.evadb, query)

        # Test index udf signature.
        index_catalog_entry = self.evadb.catalog().get_index_catalog_entry_by_name(
            "testCreateIndexName"
        )
        self.assertEqual(index_catalog_entry.type, VectorStoreType.FAISS)
        self.assertEqual(
            index_catalog_entry.save_file_path,
            self._index_save_path(),
        )

        # Test referenced column.
        input_table_entry = self.evadb.catalog().get_table_catalog_entry(
            "testCreateIndexInputTable"
        )
        input_column = [
            col for col in input_table_entry.columns if col.name == "input"
        ][0]
        self.assertEqual(index_catalog_entry.feat_column_id, input_column.row_id)
        self.assertEqual(index_catalog_entry.feat_column, input_column)

        # Test on disk index.
        try_to_import_faiss()
        import faiss

        index = faiss.read_index(index_catalog_entry.save_file_path)
        distance, row_id = index.search(np.array([[0, 0, 0]]).astype(np.float32), 1)
        self.assertEqual(distance[0][0], 0)
        self.assertEqual(row_id[0][0], 1)

        # Cleanup.
        self.evadb.catalog().drop_index_catalog_entry("testCreateIndexName")

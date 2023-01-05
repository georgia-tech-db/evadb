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
from pathlib import Path
from test.util import load_inbuilt_udfs

import faiss
import numpy as np
import pandas as pd
from mock import patch

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import ColumnType, IndexType, NdArrayType, TableType
from eva.catalog.catalog_utils import xform_column_definitions_to_catalog_entries
from eva.catalog.sql_config import IDENTIFIER_COLUMN
from eva.configuration.configuration_manager import ConfigurationManager
from eva.configuration.constants import EVA_DEFAULT_DIR, INDEX_DIR
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.parser.create_statement import ColumnDefinition
from eva.server.command_handler import execute_query_fetch_all
from eva.storage.storage_engine import StorageEngine
from eva.utils.generic_utils import generate_file_path


class CreateIndexTest(unittest.TestCase):
    def _index_save_path(self):
        return str(
            EVA_DEFAULT_DIR
            / INDEX_DIR
            / Path("{}_{}.index".format("HNSW", "testCreateIndexName"))
        )

    @classmethod
    def setUpClass(cls):
        # Bootstrap configuration manager.
        ConfigurationManager()

        # Reset catalog.
        CatalogManager().reset()

        load_inbuilt_udfs()

        # Create feature vector table and raw input table.
        feat1 = np.array([[0, 0, 0]]).astype(np.float32)
        feat2 = np.array([[100, 100, 100]]).astype(np.float32)
        feat3 = np.array([[200, 200, 200]]).astype(np.float32)

        input1 = np.array([[0, 0, 0]]).astype(np.uint8)
        input2 = np.array([[100, 100, 100]]).astype(np.uint8)
        input3 = np.array([[200, 200, 200]]).astype(np.uint8)

        # Create table.
        feat_col_list = [
            ColumnDefinition("feat", ColumnType.NDARRAY, NdArrayType.FLOAT32, (1, 3)),
        ]
        feat_col_entries = xform_column_definitions_to_catalog_entries(feat_col_list)

        input_col_list = [
            ColumnDefinition("input", ColumnType.NDARRAY, NdArrayType.UINT8, (1, 3)),
        ]
        input_col_entries = xform_column_definitions_to_catalog_entries(input_col_list)

        feat_tb_entry = CatalogManager().insert_table_catalog_entry(
            "testCreateIndexFeatTable",
            str(generate_file_path("testCreateIndexFeatTable")),
            feat_col_entries,
            identifier_column=IDENTIFIER_COLUMN,
            table_type=TableType.STRUCTURED_DATA,
        )
        storage_engine = StorageEngine.factory(feat_tb_entry)
        storage_engine.create(feat_tb_entry)

        input_tb_entry = CatalogManager().insert_table_catalog_entry(
            "testCreateIndexInputTable",
            str(generate_file_path("testCreateIndexInputTable")),
            input_col_entries,
            identifier_column=IDENTIFIER_COLUMN,
            table_type=TableType.STRUCTURED_DATA,
        )
        storage_engine = StorageEngine.factory(input_tb_entry)
        storage_engine.create(input_tb_entry)

        # Create pandas dataframe.
        feat_batch_data = Batch(
            pd.DataFrame(
                data={
                    "feat": [feat1, feat2, feat3],
                }
            )
        )
        storage_engine.write(feat_tb_entry, feat_batch_data)

        input_batch_data = Batch(
            pd.DataFrame(
                data={
                    "input": [input1, input2, input3],
                }
            )
        )
        storage_engine.write(input_tb_entry, input_batch_data)

    @classmethod
    def tearDownClass(cls):
        query = "DROP TABLE testCreateIndexFeatTable;"
        execute_query_fetch_all(query)
        query = "DROP TABLE testCreateIndexInputTable;"
        execute_query_fetch_all(query)

    def test_should_create_index(self):
        query = "CREATE INDEX testCreateIndexName ON testCreateIndexFeatTable (feat) USING HNSW;"
        execute_query_fetch_all(query)

        # Test index catalog.
        index_catalog_entry = CatalogManager().get_index_catalog_entry_by_name(
            "testCreateIndexName"
        )
        self.assertEqual(index_catalog_entry.type, IndexType.HNSW)
        self.assertEqual(
            index_catalog_entry.save_file_path,
            self._index_save_path(),
        )
        self.assertEqual(
            index_catalog_entry.udf_signature,
            None,
        )

        # Test referenced column.
        feat_table_entry = CatalogManager().get_table_catalog_entry(
            "testCreateIndexFeatTable"
        )
        feat_column = [col for col in feat_table_entry.columns if col.name == "feat"][0]
        self.assertEqual(index_catalog_entry.feat_column_id, feat_column.row_id)
        self.assertEqual(index_catalog_entry.feat_column, feat_column)

        # Test on disk index.
        index = faiss.read_index(index_catalog_entry.save_file_path)
        distance, row_id = index.search(np.array([[0, 0, 0]]).astype(np.float32), 1)
        self.assertEqual(distance[0][0], 0)
        self.assertEqual(row_id[0][0], 1)

        # Cleanup.
        CatalogManager().drop_index_catalog_entry("testCreateIndexName")

    @patch("eva.executor.create_index_executor.faiss")
    def test_should_cleanup_when_exception(self, faiss_mock):
        faiss_mock.write_index.side_effect = Exception("Test exception.")

        query = "CREATE INDEX testCreateIndexName ON testCreateIndexFeatTable (feat) USING HNSW;"
        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(query)

        # Check faulty index is not persisted on the disk
        self.assertFalse(os.path.exists(self._index_save_path()))

    def test_should_create_index_with_udf(self):
        query = "CREATE INDEX testCreateIndexName ON testCreateIndexInputTable (DummyFeatureExtractor(input)) USING HNSW;"
        execute_query_fetch_all(query)

        # Test index udf signature.
        index_catalog_entry = CatalogManager().get_index_catalog_entry_by_name(
            "testCreateIndexName"
        )
        self.assertEqual(index_catalog_entry.type, IndexType.HNSW)
        self.assertEqual(
            index_catalog_entry.save_file_path,
            self._index_save_path(),
        )
        self.assertEqual(
            index_catalog_entry.udf_signature,
            "DummyFeatureExtractor(testCreateIndexInputTable.input)",
        )

        # Test referenced column.
        input_table_entry = CatalogManager().get_table_catalog_entry(
            "testCreateIndexInputTable"
        )
        input_column = [
            col for col in input_table_entry.columns if col.name == "input"
        ][0]
        self.assertEqual(index_catalog_entry.feat_column_id, input_column.row_id)
        self.assertEqual(index_catalog_entry.feat_column, input_column)

        # Test on disk index.
        index = faiss.read_index(index_catalog_entry.save_file_path)
        distance, row_id = index.search(np.array([[0, 0, 0]]).astype(np.float32), 1)
        self.assertEqual(distance[0][0], 0)
        self.assertEqual(row_id[0][0], 1)

        # Cleanup.
        CatalogManager().drop_index_catalog_entry("testCreateIndexName")

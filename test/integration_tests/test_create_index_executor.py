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
from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from mock import patch

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import ColumnType, NdArrayType, TableType
from eva.catalog.index_type import IndexType
from eva.configuration.constants import EVA_DEFAULT_DIR, INDEX_DIR
from eva.models.storage.batch import Batch
from eva.parser.create_statement import ColConstraintInfo, ColumnDefinition
from eva.server.command_handler import execute_query_fetch_all
from eva.storage.storage_engine import StorageEngine
from eva.utils.generic_utils import generate_file_path


class CreateIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Reset catalog.
        CatalogManager().reset()

        # Create feature vector.
        feat1 = np.array([[0, 0, 0]]).astype(np.float32)
        feat2 = np.array([[100, 100, 100]]).astype(np.float32)
        feat3 = np.array([[200, 200, 200]]).astype(np.float32)

        # Create table.
        col_list = [
            ColumnDefinition(
                "feat_id", ColumnType.INTEGER, None, [], ColConstraintInfo(unique=True)
            ),
            ColumnDefinition("feat", ColumnType.NDARRAY, NdArrayType.FLOAT32, [1, 3]),
        ]
        col_metadata = [
            CatalogManager().create_column_metadata(
                col.name, col.type, col.array_type, col.dimension, col.cci
            )
            for col in col_list
        ]
        tb_metadata = CatalogManager().create_metadata(
            "testCreateIndexFeatTable",
            str(generate_file_path("testCreateIndexFeatTable")),
            col_metadata,
            identifier_column="feat_id",
            table_type=TableType.STRUCTURED_DATA,
        )
        storage_engine = StorageEngine.factory(tb_metadata)
        storage_engine.create(tb_metadata)

        # Create pandas dataframe.
        batch_data = Batch(
            pd.DataFrame(
                data={
                    "feat_id": [0, 1, 2],
                    "feat": [feat1, feat2, feat3],
                }
            )
        )
        storage_engine.write(tb_metadata, batch_data)

    @classmethod
    def tearDownClass(cls):
        query = "DROP TABLE testCreateIndexFeatTable;"
        execute_query_fetch_all(query)

    def test_should_create_index(self):
        query = "CREATE INDEX testCreateIndexName USING HNSW ON testCreateIndexFeatTable (feat);"
        execute_query_fetch_all(query)

        # Test index metadata.
        index_metadata = CatalogManager().get_index_by_name("testCreateIndexName")
        self.assertEqual(index_metadata.type, IndexType.HNSW)
        self.assertEqual(
            index_metadata.save_file_path,
            str(
                EVA_DEFAULT_DIR
                / INDEX_DIR
                / Path("{}_{}.index".format(index_metadata.type, index_metadata.name))
            ),
        )

        # Test on disk index.
        index = faiss.read_index(index_metadata.save_file_path)
        distance, logical_id = index.search(np.array([[0, 0, 0]]).astype(np.float32), 1)
        self.assertEqual(distance[0][0], 0)
        self.assertEqual(logical_id[0][0], 0)

        # Test secondary index.
        secondary_index_tb_name = "secondary_index_{}_{}".format(
            index_metadata.type, index_metadata.name
        )
        secondary_index_metadata = CatalogManager().get_dataset_metadata(
            None, secondary_index_tb_name
        )
        size = 0
        storage_engine = StorageEngine.factory(secondary_index_metadata)
        for i, batch in enumerate(storage_engine.read(secondary_index_metadata, 1)):
            df_data = batch.frames
            self.assertEqual(df_data["logical_id"][0], i)
            # Row ID is not 0 indexed.
            self.assertEqual(df_data["row_id"][0], i + 1)
            size += 1
        self.assertEqual(size, 3)

        # Cleanup.
        CatalogManager().drop_index("testCreateIndexName")
        CatalogManager().drop_dataset_metadata(None, secondary_index_tb_name)

    @patch("eva.executor.create_index_executor.faiss")
    def test_should_cleanup_when_exception(self, faiss_mock):
        faiss_mock.write_index.side_effect = Exception("Test exception.")

        query = "CREATE INDEX testCreateIndexName USING HNSW ON testCreateIndexFeatTable (feat);"
        with self.assertRaises(Exception):
            execute_query_fetch_all(query)

        # Check secondary index is dropped.
        secondary_index_tb_name = "secondary_index_{}_{}".format(
            "HNSW", "testCreateIndexName"
        )
        self.assertFalse(
            CatalogManager().check_table_exists(None, secondary_index_tb_name)
        )

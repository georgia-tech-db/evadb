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

import faiss
import numpy as np
import pandas as pd
import pytest

from evadb.catalog.catalog_type import VectorStoreType
from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all
from evadb.storage.storage_engine import StorageEngine
from evadb.udfs.udf_bootstrap_queries import Text_feat_udf_query


@pytest.mark.notparallel
class CreateIndexTest(unittest.TestCase):
    def _index_save_path(self, name="testCreateIndexName"):
        return str(
            Path(self.evadb.config.get_value("storage", "index_dir"))
            / Path("{}_{}.index".format("FAISS", name))
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
        index = faiss.read_index(index_catalog_entry.save_file_path)
        distance, row_id = index.search(np.array([[0, 0, 0]]).astype(np.float32), 1)
        self.assertEqual(distance[0][0], 0)
        self.assertEqual(row_id[0][0], 1)

        # Cleanup.
        self.evadb.catalog().drop_index_catalog_entry("testCreateIndexName")

    def test_aashould_create_index_with_udf_on_doc_table(self):
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MYPDFs;")
        pdf_path1 = f"{EvaDB_ROOT_DIR}/data/documents/pdf_sample1.pdf"
        pdf_path2 = f"{EvaDB_ROOT_DIR}/data/documents/one_page.pdf"
        execute_query_fetch_all(self.evadb, f"LOAD DOCUMENT '{pdf_path1}' INTO MyPDFs;")
        execute_query_fetch_all(self.evadb, f"LOAD DOCUMENT '{pdf_path2}' INTO MyPDFs;")

        execute_query_fetch_all(self.evadb, Text_feat_udf_query)

        self.evadb.config.update_value("experimental", "ray", False)
        query = "CREATE INDEX doc_index ON MyPDFs (SentenceFeatureExtractor(data)) USING FAISS;"
        execute_query_fetch_all(self.evadb, query)

        # Test index udf signature.
        index_catalog_entry = self.evadb.catalog().get_index_catalog_entry_by_name(
            "doc_index"
        )
        self.assertEqual(index_catalog_entry.type, VectorStoreType.FAISS)
        self.assertEqual(
            index_catalog_entry.save_file_path,
            self._index_save_path("doc_index"),
        )

        # get tuples in the MyPDFs
        df = execute_query_fetch_all(self.evadb, "select * from MyPDFs;").frames
        num_tuples_per_file = [len(df[df["mypdfs._row_id"] == i]) for i in range(2)]

        # Test if index has correct number of tuples
        index = faiss.read_index(index_catalog_entry.save_file_path)
        self.assertEqual(index.ntotal, len(df))

        # check if correct ids are added to the index
        # Note: reconstruct might not work for all the FAISS index types
        # https://github.com/facebookresearch/faiss/issues/1043
        from evadb.constants import MAGIC_NUMBER

        for i, num_tuples in enumerate(num_tuples_per_file):
            for j in range(num_tuples):
                idx = i * MAGIC_NUMBER + j
                # this should not raise any exception
                index.reconstruct(idx)

        # Cleanup.
        execute_query_fetch_all(self.evadb, "DROP INDEX IF EXISTS doc_index;")
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MYPDFs;")


if __name__ == "__main__":
    unittest.main()

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
from test.util import create_sample_video, file_remove, load_inbuilt_udfs

import numpy as np
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all
from eva.catalog.catalog_type import ColumnType, IndexType, NdArrayType, TableType
from eva.configuration.constants import EVA_ROOT_DIR
from eva.catalog.catalog_utils import xform_column_definitions_to_catalog_entries
from eva.catalog.sql_config import IDENTIFIER_COLUMN
from eva.configuration.configuration_manager import ConfigurationManager
from eva.parser.create_statement import ColumnDefinition
from eva.utils.generic_utils import generate_file_path
from eva.models.storage.batch import Batch
from eva.storage.storage_engine import StorageEngine


class DeleteExecutorTest(unittest.TestCase):
    def setUp(self):
        # Bootstrap configuration manager.
        ConfigurationManager()

        # Reset catalog.
        CatalogManager().reset()

        load_inbuilt_udfs()

        #########################################################
        # Create a table for testing Delete with Structured Data#
        #########################################################
        id1 = 5
        id2 = 15
        id3 = 25

        feat1 = np.array([[0, 0, 0]]).astype(np.float32)
        feat2 = np.array([[100, 100, 100]]).astype(np.float32)
        feat3 = np.array([[200, 200, 200]]).astype(np.float32)

        input1 = np.array([[0, 0, 0]]).astype(np.uint8)
        input2 = np.array([[100, 100, 100]]).astype(np.uint8)
        input3 = np.array([[200, 200, 200]]).astype(np.uint8)

        # Create table.
        feat_col_list = [
            ColumnDefinition("id", ColumnType.INTEGER, None, None),
            ColumnDefinition("feat", ColumnType.NDARRAY, None, (1, 3)),
            ColumnDefinition("input", ColumnType.NDARRAY, None, (1, 3)),
        ]
        feat_col_entries = xform_column_definitions_to_catalog_entries(feat_col_list)

        input_col_list = [
            ColumnDefinition("id", ColumnType.INTEGER, None, None),
            ColumnDefinition("feat", ColumnType.NDARRAY, None, (1, 3)),
            ColumnDefinition("input", ColumnType.NDARRAY, None, (1, 3)),
        ]
        input_col_entries = xform_column_definitions_to_catalog_entries(input_col_list)

        feat_tb_entry = CatalogManager().insert_table_catalog_entry(
            "testDeleteOne",
            str(generate_file_path("testDeleteOne")),
            feat_col_entries,
            identifier_column=IDENTIFIER_COLUMN,
            table_type=TableType.STRUCTURED_DATA,
        )
        storage_engine = StorageEngine.factory(feat_tb_entry)
        storage_engine.create(feat_tb_entry)

        input_tb_entry = CatalogManager().insert_table_catalog_entry(
            "testDeleteTwo",
            str(generate_file_path("testDeleteTwo")),
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
                    "id":   [id1, id2, id3],
                    "feat": [feat1, feat2, feat3],
                    "input": [input1, input2, input3],
                }
            )
        )
        storage_engine.write(feat_tb_entry, feat_batch_data)

        input_batch_data = Batch(
            pd.DataFrame(
                data={
                    "id":   [id1, id2, id3],
                    "feat": [feat1, feat2, feat3],
                    "input": [input1, input2, input3],
                }
            )
        )
        storage_engine.write(input_tb_entry, input_batch_data)

        ####################################################
        # Create a table for testing Delete with Video Data#
        ####################################################

        path = f"{EVA_ROOT_DIR}/data/sample_videos/1/*.mp4"
        query = f'LOAD VIDEO "{path}" INTO TestDeleteVideos;'
        result = execute_query_fetch_all(query)



    def tearDown(self):
        file_remove("dummy.avi")

    # integration test
    @unittest.skip("Not supported in current version")
    def test_should_delete_single_video_in_table(self):

        path = f"{EVA_ROOT_DIR}/data/sample_videos/1/2.mp4"
        delete_query = f"""DELETE FROM TestDeleteVideos WHERE name="{path}";"""
        batch = execute_query_fetch_all(delete_query)

        query = "SELECT name FROM MyVideo"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[40, 40, 40], [40, 40, 40]], [[40, 40, 40], [40, 40, 40]]]),
            )
        )

        query = "SELECT id, data FROM MyVideo WHERE id = 41;"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[41, 41, 41], [41, 41, 41]], [[41, 41, 41], [41, 41, 41]]]),
            )
        )
    
    @unittest.skip("Not supported in current version")
    def test_should_delete_single_image_in_table(self):
        path = f"{EVA_ROOT_DIR}/data/sample_videos/1/2.mp4"
        delete_query = f"""DELETE FROM TestDeleteVideos WHERE name="{path}";"""
        batch = execute_query_fetch_all(delete_query)

        query = "SELECT name FROM MyVideo"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[40, 40, 40], [40, 40, 40]], [[40, 40, 40], [40, 40, 40]]]),
            )
        )

        query = "SELECT id, data FROM MyVideo WHERE id = 41;"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[41, 41, 41], [41, 41, 41]], [[41, 41, 41], [41, 41, 41]]]),
            )
        )

    def test_should_delete_tuple_in_table(self):
        delete_query = "DELETE FROM testDeleteOne WHERE id=5;"
        batch = execute_query_fetch_all(delete_query)
        delete_query_2 = "DELETE FROM testDeleteTwo WHERE id<20;"
        batch = execute_query_fetch_all(delete_query_2)

        query = "SELECT * FROM testDeleteOne;"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["testdeleteone.id"].array,
                np.array([15, 25], dtype=np.int64),
            )
        )

        query = "SELECT id, feat FROM testDeleteTwo;"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["testdeletetwo.id"].array,
                np.array([15, 25], dtype=np.int64),
            )
        )

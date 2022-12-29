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
from test.util import create_sample_image, file_remove, load_inbuilt_udfs

import numpy as np
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all
from eva.storage.storage_engine import StorageEngine


class OpenTests(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        ConfigurationManager()
        # Load built-in UDFs.
        load_inbuilt_udfs()

        # Insert image path.
        create_sample_image()
        create_table_query = "CREATE TABLE IF NOT EXISTS testOpenTable (num INTEGER);"
        execute_query_fetch_all(create_table_query)

        # Insert dummy data into table.
        table_catalog_entry = CatalogManager().get_table_catalog_entry("testOpenTable")
        storage_engine = StorageEngine().factory(table_catalog_entry)
        storage_engine.write(
            table_catalog_entry, Batch(pd.DataFrame([{"num": 1}, {"num": 2}]))
        )

    def tearDown(self):
        file_remove("dummy.jpg")

        # Drop table.
        drop_table_query = "DROP TABLE testOpenTable;"
        execute_query_fetch_all(drop_table_query)

    def test_open_should_open_image(self):
        # Test query runs successfully with Open function call.
        config = ConfigurationManager()
        upload_dir_from_config = config.get_value("storage", "upload_dir")
        img_path = os.path.join(upload_dir_from_config, "dummy.jpg")
        select_query = """SELECT num, Open("{}") FROM testOpenTable;""".format(img_path)
        batch_res = execute_query_fetch_all(select_query)

        expected_img = np.array(np.ones((3, 3, 3)), dtype=np.float32)
        expected_img[0] -= 1
        expected_img[2] += 1

        expected_batch = Batch(
            pd.DataFrame(
                {"testopentable.num": [1, 2], "open.data": [expected_img, expected_img]}
            )
        )
        self.assertEqual(expected_batch, batch_res)

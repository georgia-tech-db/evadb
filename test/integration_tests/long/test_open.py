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
from test.util import (
    create_sample_image,
    file_remove,
    get_evadb_for_testing,
    load_udfs_for_testing,
    shutdown_ray,
)

import numpy as np
import pandas as pd
import pytest

from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all
from evadb.storage.storage_engine import StorageEngine


@pytest.mark.notparallel
class OpenTests(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        # Load built-in UDFs.
        load_udfs_for_testing(self.evadb, mode="debug")

        # Insert image path.
        self.img_path = create_sample_image()
        create_table_query = "CREATE TABLE IF NOT EXISTS testOpenTable (num INTEGER);"
        execute_query_fetch_all(self.evadb, create_table_query)

        # Insert dummy data into table.
        table_catalog_entry = self.evadb.catalog().get_table_catalog_entry(
            "testOpenTable"
        )
        storage_engine = StorageEngine.factory(self.evadb, table_catalog_entry)
        storage_engine.write(
            table_catalog_entry, Batch(pd.DataFrame([{"num": 1}, {"num": 2}]))
        )

    def tearDown(self):
        shutdown_ray()

        file_remove("dummy.jpg")

        # Drop table.
        drop_table_query = "DROP TABLE testOpenTable;"
        execute_query_fetch_all(self.evadb, drop_table_query)

    def test_open_should_open_image(self):
        # Test query runs successfully with Open function call.
        select_query = """SELECT num, Open("{}") FROM testOpenTable;""".format(
            self.img_path
        )
        batch_res = execute_query_fetch_all(self.evadb, select_query)

        expected_img = np.array(np.ones((3, 3, 3)), dtype=np.float32)
        expected_img[0] -= 1
        expected_img[2] += 1

        expected_batch = Batch(
            pd.DataFrame(
                {"testopentable.num": [1, 2], "open.data": [expected_img, expected_img]}
            )
        )
        self.assertEqual(expected_batch, batch_res)

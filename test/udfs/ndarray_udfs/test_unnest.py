# coding=utf-8
# Copyright 2018-2020 EVA
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
import pandas as pd

from src.catalog.catalog_manager import CatalogManager
from src.models.storage.batch import Batch
from src.udfs.ndarray_udfs.unnest import Unnest
from test.util import perform_query
from test.util import populate_catalog_with_built_in_udfs


class UnnestTests(unittest.TestCase):

    def setUp(self):
        CatalogManager().reset()
        populate_catalog_with_built_in_udfs()

        load_query = """LOAD DATA INFILE 'data/ua_detrac/ua_detrac.mp4'
                        INTO MyVideo;"""
        perform_query(load_query)


    def test_should_unnest_dataframe(self):
        query = """SELECT FastRCNNObjectDetector(data).labels FROM
                    MyVideo WHERE id < 2;"""
        without_unnest_batch = perform_query(query)
        query = """SELECT Unnest(FastRCNNObjectDetector(data).labels) FROM
                    MyVideo WHERE id < 2;"""
        unnest_batch = perform_query(query)
        expected = Batch(Unnest().exec(without_unnest_batch.frames))
        self.assertEqual(unnest_batch, expected)


if __name__ == "__main__":
    unittest.main()

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
from test.util import perform_query
from src.models.storage.batch import Batch


class MaterializedViewTest(unittest.TestCase):

    def setUp(self):
        CatalogManager().reset()

    def test_should_materlizied_view(self):
        query = """LOAD DATA INFILE 'data/ua_detrac/ua_detrac.mp4'
                   INTO MyVideo;"""
        perform_query(query)

        create_udf_query = """CREATE UDF FastRCNNObjectDetector
                  INPUT  (Frame_Array NDARRAY (3, 256, 256))
                  OUTPUT (label TEXT(10), pred_score INTEGER, pre_boxes NDARRAY(4))
                  TYPE  Classification
                  IMPL  'src/udfs/fastrcnn_object_detector.py';
        """
        perform_query(create_udf_query)

        select_query = """SELECT id, FastRCNNObjectDetector(data).label FROM MyVideo WHERE id < 5;"""
        query = 'CREATE MATERIALIZED VIEW uadtrac_fastRCNN (id, label) AS {}' \
            .format(select_query)
        perform_query(query)

        query = 'SELECT id, label FROM uadtrac_fastRCNN;'
        actual_batch = perform_query(select_query)
        actual_batch.sort()
        expected_batch = Batch(
                frames=pd.DataFrame([{'id': i, 'label': 'person'} for i in range(5)])
        )
        self.assertEqual(actual_batch, expected_batch)

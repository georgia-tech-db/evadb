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
from test.markers import ocr_skip_marker
from test.util import get_evadb_for_testing, shutdown_ray

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.server.command_handler import execute_query_fetch_all


class LikeTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()
        meme1 = f"{EvaDB_ROOT_DIR}/data/detoxify/meme1.jpg"
        meme2 = f"{EvaDB_ROOT_DIR}/data/detoxify/meme2.jpg"

        execute_query_fetch_all(self.evadb, f"LOAD IMAGE '{meme1}' INTO MemeImages;")
        execute_query_fetch_all(self.evadb, f"LOAD IMAGE '{meme2}' INTO MemeImages;")

    def tearDown(self):
        shutdown_ray()
        # clean up
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MemeImages;")

    @ocr_skip_marker
    def test_like_with_ocr(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(10),
                          bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  OCRExtraction
                  IMPL  'evadb/udfs/ocr_extractor.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)
        select_query = """SELECT X.label, X.x, X.y FROM MemeImages JOIN LATERAL UNNEST(OCRExtractor(data)) AS X(label, x, y) WHERE label LIKE {};""".format(
            r"""'.*SWAG.*'"""
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(len(actual_batch), 1)

    @ocr_skip_marker
    def test_like_fails_on_non_string_col(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(10),
                          bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  OCRExtraction
                  IMPL  'evadb/udfs/ocr_extractor.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query = """SELECT * FROM MemeImages JOIN LATERAL UNNEST(OCRExtractor(data)) AS X(label, x, y) WHERE x LIKE "[A-Za-z]*CANT";"""
        with self.assertRaises(Exception):
            execute_query_fetch_all(self.evadb, select_query)

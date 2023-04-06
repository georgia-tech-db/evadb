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
from test.util import shutdown_ray

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.server.command_handler import execute_query_fetch_all


class LikeTest(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        meme1 = f"{EVA_ROOT_DIR}/data/detoxify/meme1.jpg"
        meme2 = f"{EVA_ROOT_DIR}/data/detoxify/meme2.jpg"

        execute_query_fetch_all(f"LOAD IMAGE '{meme1}' INTO MemeImages;")
        execute_query_fetch_all(f"LOAD IMAGE '{meme2}' INTO MemeImages;")

    def tearDown(self):
        shutdown_ray()
        # clean up
        execute_query_fetch_all("DROP TABLE IF EXISTS MemeImages;")

    def test_like_with_ocr(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(10),
                          bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  OCRExtraction
                  IMPL  'eva/udfs/ocr_extractor.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = (
            """SELECT * FROM MemeImages JOIN LATERAL OCRExtractor(data) AS X(label, x, y) WHERE label LIKE """
            + r'"[A-Za-z\', \[]*CANT[\,\',A-Za-z \]]*"'
        )
        actual_batch = execute_query_fetch_all(select_query)

        self.assertEqual(len(actual_batch._frames), 2)

    def test_like_fails_on_non_string_col(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(10),
                          bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  OCRExtraction
                  IMPL  'eva/udfs/ocr_extractor.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT * FROM MemeImages JOIN LATERAL OCRExtractor(data) AS X(label, x, y) WHERE x LIKE "[A-Za-z]*CANT";"""
        with self.assertRaises(Exception):
            execute_query_fetch_all(select_query)


if __name__ == "__main__":
    unittest.main()

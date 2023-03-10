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
from test.util import (
    create_dummy_batches,
    create_sample_csv,
    create_sample_video,
    file_remove,
    load_inbuilt_udfs,
)

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.server.command_handler import execute_query_fetch_all


class LikeTest(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        self.video_file_path = create_sample_video()
        mnist = f"{EVA_ROOT_DIR}/data/mnist/mnist.mp4"
        execute_query_fetch_all(f"LOAD VIDEO '{mnist}' INTO MNIST;")
        self.image_files_path = Path(
            f"{EVA_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/*.jpg"
        )
        create_sample_csv()

    def tearDown(self):
        file_remove("dummy.avi")
        file_remove("dummy.csv")
        # clean up
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

    # integration test for load video
    def test_like_with_ocr(self):
        query = f"LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(query)

        create_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(10),
                          bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  OCRExtraction
                  IMPL  'eva/udfs/ocr_extractor.py';
        """
        execute_query_fetch_all(create_udf_query)

        ocr_query = """SELECT OCRExtractor(data) FROM MNIST
                        WHERE id >= 150 AND id < 155;"""

        select_query = """SELECT * FROM MyVideo WHERE name LIKE "/Users%";"""

        actual_batch = execute_query_fetch_all(select_query)
        actual_batch = execute_query_fetch_all(ocr_query)
        
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())[0]
        # self.assertEqual(actual_batch, expected_batch)
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

  

if __name__ == "__main__":
    unittest.main()

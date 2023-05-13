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
    create_sample_video,
    file_remove,
    shutdown_ray,
)

import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class OverwriteExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        video_file_path = create_sample_video()
        image_file_path = Path(
            f"{EVA_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/img00001.jpg"
        )
        udf_path = Path(f"{EVA_ROOT_DIR}/eva/udfs/ndarray/gaussian_blur.py")
        create_udf_query = f"CREATE UDF IF NOT EXISTS GaussianBlur INPUT (frame NDARRAY UINT8(3, ANYDIM, ANYDIM)) OUTPUT (blurred_frame_array NDARRAY UINT8(3, ANYDIM, ANYDIM)) TYPE ndarray IMPL '{udf_path}';"
        execute_query_fetch_all(create_udf_query)

        query = f"LOAD VIDEO '{video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(query)

        overwrite_query = "OVERWRITE MyVideo BY GaussianBlur(data);"
        execute_query_fetch_all(overwrite_query)

        query = f"LOAD IMAGE '{image_file_path}' INTO MyImage;"
        execute_query_fetch_all(query)

        overwrite_query = "OVERWRITE MyImage BY GaussianBlur(data);"
        execute_query_fetch_all(overwrite_query)

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()
        file_remove("dummy.avi")
        file_remove(Path(
            f"{EVA_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/modified_img00001.jpg"
        ))
        # clean up
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")
        execute_query_fetch_all("DROP TABLE IF EXISTS MyImage;")
        execute_query_fetch_all("DROP UDF IF EXISTS GaussianBlur;")

    # integration test for overwrite
    def test_should_overwrite_video(self):
        select_query = "SELECT * FROM MyVideo;"
        actual_batch = execute_query_fetch_all(select_query)
        modified_dir = actual_batch.column_as_numpy_array(actual_batch.columns[1])[0]
        self.assertTrue("tmp/modified/dummy.avi" in modified_dir)

    def test_should_overwrite_image(self):
        select_query = "SELECT * FROM MyImage;"
        actual_batch = execute_query_fetch_all(select_query)
        modified_dir = actual_batch.column_as_numpy_array(actual_batch.columns[1])[0]
        self.assertTrue("modified_img00001.jpg" in modified_dir)

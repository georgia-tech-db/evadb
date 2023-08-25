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
import os
import unittest
from test.markers import (
    gpu_skip_marker,
    ocr_skip_marker,
    ray_skip_marker,
    windows_skip_marker,
)
from test.util import (
    create_sample_video,
    file_remove,
    get_evadb_for_testing,
    load_udfs_for_testing,
    shutdown_ray,
)

import numpy as np
import pandas.testing as pd_testing
import pytest

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all
from evadb.udfs.udf_bootstrap_queries import Asl_udf_query, Mvit_udf_query
from evadb.utils.generic_utils import try_to_import_cv2


@pytest.mark.notparallel
class PytorchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()
        os.environ["ray"] = str(cls.evadb.config.get_value("experimental", "ray"))

        ua_detrac = f"{EvaDB_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"

        execute_query_fetch_all(cls.evadb, f"LOAD VIDEO '{ua_detrac}' INTO MyVideo;")
        load_udfs_for_testing(cls.evadb)

    @classmethod
    def tearDownClass(cls):
        file_remove("ua_detrac.mp4")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MyVideo;")

    def assertBatchEqual(self, a: Batch, b: Batch, msg: str):
        try:
            pd_testing.assert_frame_equal(a.frames, b.frames)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def setUp(self):
        self.addTypeEqualityFunc(Batch, self.assertBatchEqual)

    def tearDown(self) -> None:
        shutdown_ray()

    def test_check_unnest_with_predicate_on_yolo(self):
        query = """SELECT id, Yolo.label, Yolo.bbox, Yolo.score
                  FROM MyVideo
                  JOIN LATERAL UNNEST(Yolo(data)) AS Yolo(label, bbox, score)
                  WHERE Yolo.label = 'car' AND id < 2;"""

        actual_batch = execute_query_fetch_all(self.evadb, query)

        # due to unnest the number of returned tuples should be at least > 10
        self.assertTrue(len(actual_batch) > 2)


if __name__ == "__main__":
    unittest.main()

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
import time
import unittest
from pathlib import Path
from test.util import (
    create_sample_image,
    is_ray_stage_running,
    load_udfs_for_testing,
    shutdown_ray,
)

import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.executor_utils import ExecutorError
from eva.server.command_handler import execute_query_fetch_all


@pytest.mark.skipif(
    not ConfigurationManager().get_value("experimental", "ray"),
    reason="Only test for ray execution.",
)
class ErrorHandlingRayTests(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        ConfigurationManager()
        # Load built-in UDFs.
        load_udfs_for_testing(mode="minimal")

        # Deliberately create a faulty path.
        img_path = create_sample_image()
        execute_query_fetch_all(f"LOAD IMAGE '{img_path}' INTO testRayErrorHandling;")

        # Forcefully remove file to cause error.
        Path(img_path).unlink()

    def tearDown(self):
        shutdown_ray()

        # Drop table.
        drop_table_query = "DROP TABLE testRayErrorHandling;"
        execute_query_fetch_all(drop_table_query)

    def test_ray_error_populate_to_all_stages(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS ToxicityClassifier
                  INPUT  (text NDARRAY STR(100))
                  OUTPUT (labels NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'eva/udfs/toxicity_classifier.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT ToxicityClassifier(data) FROM testRayErrorHandling;"""

        with self.assertRaises(ExecutorError):
            _ = execute_query_fetch_all(select_query)

        time.sleep(3)
        self.assertFalse(is_ray_stage_running())

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
import time
import unittest
from pathlib import Path
from test.markers import ray_skip_marker
from test.util import (
    create_sample_image,
    get_evadb_for_testing,
    is_ray_stage_running,
    load_udfs_for_testing,
    shutdown_ray,
)

from evadb.executor.executor_utils import ExecutorError
from evadb.server.command_handler import execute_query_fetch_all


class ErrorHandlingRayTests(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        os.environ["ray"] = str(self.evadb.config.get_value("experimental", "ray"))
        self.evadb.catalog().reset()
        # Load built-in UDFs.
        load_udfs_for_testing(self.evadb, mode="debug")

        # Deliberately create a faulty path.
        img_path = create_sample_image()
        execute_query_fetch_all(
            self.evadb, f"LOAD IMAGE '{img_path}' INTO testRayErrorHandling;"
        )

        # Forcefully remove file to cause error.
        Path(img_path).unlink()

    def tearDown(self):
        shutdown_ray()

        # Drop table.
        drop_table_query = "DROP TABLE testRayErrorHandling;"
        execute_query_fetch_all(self.evadb, drop_table_query)

    @ray_skip_marker
    def test_ray_error_populate_to_all_stages(self):
        udf_name, task = "HFObjectDetector", "image-classification"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' '{task}'
        """

        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query = """SELECT HFObjectDetector(data) FROM testRayErrorHandling;"""

        with self.assertRaises(ExecutorError):
            _ = execute_query_fetch_all(self.evadb, select_query)

        time.sleep(3)
        self.assertFalse(is_ray_stage_running())

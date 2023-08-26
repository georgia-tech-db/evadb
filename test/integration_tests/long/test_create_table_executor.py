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
from test.markers import macos_skip_marker
from test.util import (
    DummyObjectDetector,
    create_sample_video,
    file_remove,
    get_evadb_for_testing,
    load_udfs_for_testing,
    shutdown_ray,
)

import pandas as pd
import pytest

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


class CreateTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        cls.evadb.catalog().reset()
        video_file_path = create_sample_video()
        load_query = f"LOAD VIDEO '{video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(cls.evadb, load_query)
        ua_detrac = f"{EvaDB_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        execute_query_fetch_all(cls.evadb, f"LOAD VIDEO '{ua_detrac}' INTO UATRAC;")
        load_udfs_for_testing(cls.evadb)

    @classmethod
    def tearDownClass(cls):
        file_remove("dummy.avi")
        file_remove("ua_detrac.mp4")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MyVideo;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS UATRAC;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS uadtrac_fastRCNN;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS dummy_table;")
        shutdown_ray()

    def _test_currently_cannot_create_boolean_table(self):
        query = """ CREATE TABLE BooleanTable( A BOOLEAN);"""

        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(self.evadb, query)

    @macos_skip_marker
    def test_should_create_table_from_select(self):
        create_query = """CREATE TABLE dummy_table
            AS SELECT id, DummyObjectDetector(data).label FROM MyVideo;
        """
        execute_query_fetch_all(self.evadb, create_query)

        select_query = "SELECT id, label FROM dummy_table;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()

        labels = DummyObjectDetector().labels
        expected = [
            {"dummy_table.id": i, "dummy_table.label": [labels[1 + i % 2]]}
            for i in range(NUM_FRAMES)
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

    @macos_skip_marker
    @pytest.mark.torchtest
    def test_should_create_table_from_select_lateral_join(self):
        select_query = (
            "SELECT id, label, bbox FROM UATRAC JOIN LATERAL "
            "Yolo(data) AS T(label, bbox, score) WHERE id < 5;"
        )
        query = "CREATE TABLE IF NOT EXISTS " f"uadtrac_fastRCNN AS {select_query};"
        execute_query_fetch_all(self.evadb, query)

        select_view_query = "SELECT id, label, bbox FROM uadtrac_fastRCNN"
        actual_batch = execute_query_fetch_all(self.evadb, select_view_query)
        actual_batch.sort()

        self.assertEqual(len(actual_batch), 5)
        # non-trivial test case
        res = actual_batch.frames
        for idx in res.index:
            self.assertTrue("car" in res["uadtrac_fastrcnn.label"][idx])


if __name__ == "__main__":
    unittest.main()

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
from test.util import shutdown_ray, suffix_pytest_xdist_worker_id_to_dir

import pytest

from evadb.configuration.constants import EvaDB_DATABASE_DIR, EvaDB_ROOT_DIR
from evadb.interfaces.relational.db import connect
from evadb.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class SaliencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_dir = suffix_pytest_xdist_worker_id_to_dir(EvaDB_DATABASE_DIR)
        cls.conn = connect(cls.db_dir)
        cls.evadb = cls.conn._evadb

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()
        # execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS SALIENCY;")
        # file_remove("dummy.avi")

    @unittest.skip("Not supported in current version")
    def test_saliency(self):
        Saliency1 = f"{EvaDB_ROOT_DIR}/data/saliency/test1.jpeg"
        create_udf_query = f"LOAD IMAGE '{Saliency1}' INTO SALIENCY;"

        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS SALIENCY;")

        execute_query_fetch_all(self.evadb, create_udf_query)
        execute_query_fetch_all(
            self.evadb, "DROP UDF IF EXISTS SaliencyFeatureExtractor"
        )

        create_udf_query = f"""CREATE UDF IF NOT EXISTS SaliencyFeatureExtractor
                    IMPL  '{EvaDB_ROOT_DIR}/evadb/udfs/saliency_feature_extractor.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query_saliency = """SELECT data, SaliencyFeatureExtractor(data)
                  FROM SALIENCY
        """
        actual_batch_saliency = execute_query_fetch_all(
            self.evadb, select_query_saliency
        )
        self.assertEqual(len(actual_batch_saliency.columns), 2)

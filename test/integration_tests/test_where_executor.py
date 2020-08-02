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
import os
import cv2
import numpy as np
import pandas as pd

from src.parser.parser import Parser
from src.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from src.optimizer.plan_generator import PlanGenerator
from src.executor.plan_executor import PlanExecutor
from src.catalog.catalog_manager import CatalogManager
from src.models.storage.batch import Batch
from src.storage import StorageEngine
from test.util import custom_list_of_dicts_equal
from src.catalog.models.base_model import drop_db

from test.util import create_sample_video
from test.util import create_dummy_batches

NUM_FRAMES = 10


class WhereExecutorTest(unittest.TestCase):

    def setUp(self):
        create_sample_video()

    def tearDown(self):
        os.remove('dummy.avi')

    def perform_query(self, query):
        stmt = Parser().parse(query)[0]
        l_plan = StatementToPlanConvertor().visit(stmt)
        p_plan = PlanGenerator().build(l_plan)
        return PlanExecutor(p_plan).execute_plan()

    # integration test
    def test_select_and_where_video_in_table(self):
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""

        self.perform_query(load_query)

        select_query = "SELECT id,data FROM MyVideo WHERE id = 5;"
        actual_batch = self.perform_query(select_query)
        expected_rows = [{"id" : 5,
                          "data": np.array(np.ones((2, 2, 3))
                                    * 0.1 * float(5 + 1) * 255,
                                    dtype=np.uint8)}]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertTrue(actual_batch, expected_batch)

        select_query = "SELECT data FROM MyVideo WHERE id = 5;"
        actual_batch = self.perform_query(select_query)
        expected_rows = [{"data": np.array(np.ones((2, 2, 3))
                                    * 0.1 * float(5 + 1) * 255,
                                    dtype=np.uint8)}]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertTrue(actual_batch, expected_batch)

        # Arithmetic operation is not supported yet

if __name__ == "n__":
    unittest.main()

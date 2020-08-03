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
import pandas as pd
import numpy as np

from src.parser.parser import Parser
from src.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from src.optimizer.plan_generator import PlanGenerator
from src.executor.plan_executor import PlanExecutor
from src.catalog.catalog_manager import CatalogManager
from src.models.storage.batch import Batch
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.inference.outcome import Outcome
from src.udfs.abstract_udfs import AbstractClassifierUDF
from test.util import create_sample_video
from typing import List


class DummyObjectDetector(AbstractClassifierUDF):

    @property
    def name(self) -> str:
        return "dummyObjectDetector"

    def __init__(self):
        super().__init__()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return ['__background__', 'person', 'bicycle']

    def classify(self, frames: np.ndarray) -> List[Outcome]:
        if (frames == np.array(np.ones((2, 2, 3)) * 0.1 * float(5 + 1) * 255,
                               dtype=np.uint8)).all():
            label = self.labels[1]
        else:
            label = self.labels[2]
        prediction_df_list = [Outcome(
            pd.DataFrame([{'label': [label, 'apple']}]), 'label')]
        return prediction_df_list


NUM_FRAMES = 10


class UDFExecutorTest(unittest.TestCase):

    def setUp(self):
        CatalogManager().reset()
        create_sample_video()

    def tearDown(self):
        os.remove('dummy.avi')

    def perform_query(self, query):
        stmt = Parser().parse(query)[0]
        l_plan = StatementToPlanConvertor().visit(stmt)
        p_plan = PlanGenerator().build(l_plan)
        return PlanExecutor(p_plan).execute_plan()

    # integration test
    def test_should_load_and_select_and_udf_video_in_table(self):
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""

        self.perform_query(load_query)

        create_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY (3, 256, 256))
                  OUTPUT (Labels NDARRAY (10))
                  TYPE  Classification
                  IMPL  'test/integration_tests/test_udf_executor.py';
        """
        self.perform_query(create_udf_query)

        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo;"
        actual_batch = self.perform_query(select_query)

        expected = [{'id': i, 'label': ['bicycle', 'apple']}
                    for i in range(NUM_FRAMES)]
        expected[5]['label'][0] = 'person'
        expected_batch = Batch(frames=pd.DataFrame(expected))

        self.assertTrue(actual_batch, expected_batch)


if __name__ == "__main__":
    unittest.main()

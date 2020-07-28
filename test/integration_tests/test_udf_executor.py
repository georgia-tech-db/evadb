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

from src.parser.parser import Parser
from src.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from src.optimizer.plan_generator import PlanGenerator
from src.executor.plan_executor import PlanExecutor
from src.catalog.catalog_manager import CatalogManager
from src.storage import StorageEngine
from test.util import custom_list_of_dicts_equal
from src.catalog.models.base_model import drop_db

NUM_FRAMES = 10


class UDFExecutorTest(unittest.TestCase):

    def create_sample_video(self):
        try:
            os.remove('dummy.avi')
        except FileNotFoundError:
            pass

        out = cv2.VideoWriter('dummy.avi',
                              cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                              (2, 2))
        for i in range(NUM_FRAMES):
            frame = np.array(np.ones((2, 2, 3)) * 0.1 * float(i + 1) * 255,
                             dtype=np.uint8)
            out.write(frame)

    def create_dummy_frames(self, num_frames=NUM_FRAMES, filters=[]):
        if not filters:
            filters = range(num_frames)
        for i in filters:
            yield {'id': i,
                   'data': np.array(np.ones((2, 2, 3))
                                    * 0.1 * float(i + 1) * 255,
                                    dtype=np.uint8)}

    def setUp(self):
        self.create_sample_video()
        try:
            drop_db()
        except:
            pass

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
                  IMPL  'src/udfs/dummy_object_detector.py';
        """
        self.perform_query(create_udf_query)

        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo;"
        batch = self.perform_query(select_query)

        return_rows = batch.frames.to_dict('records')
        dummy_frames = [{'id' : i, 'label' : ['bicycle', 'apple']} for i in range(NUM_FRAMES)]
        dummy_frames[5]['label'][0] = 'person'

        self.assertEqual(len(return_rows), NUM_FRAMES)
        self.assertTrue(custom_list_of_dicts_equal(dummy_frames, return_rows))


if __name__ == "__main__":
    unittest.main()

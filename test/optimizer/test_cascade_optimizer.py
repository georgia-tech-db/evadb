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
from test.util import NUM_FRAMES, create_sample_video, file_remove, shutdown_ray

import pandas as pd
import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.experimental.ray.planner.exchange_plan import ExchangePlan
from eva.models.storage.batch import Batch
from eva.optimizer.plan_generator import PlanGenerator
from eva.plan_nodes.nested_loop_join_plan import NestedLoopJoinPlan
from eva.plan_nodes.project_plan import ProjectPlan
from eva.plan_nodes.storage_plan import StoragePlan
from eva.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class CascadeOptimizer(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        self.video_file_path = create_sample_video(NUM_FRAMES)

    def tearDown(self):
        shutdown_ray()
        file_remove("dummy.avi")

    def test_logical_to_physical_udf(self):
        load_query = f"LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(load_query)

        create_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT id, DummyObjectDetector(data)
                    FROM MyVideo
                    WHERE DummyObjectDetector(data).label = ['person'];
        """
        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected = [
            {"myvideo.id": i * 2, "dummyobjectdetector.label": ["person"]}
            for i in range(NUM_FRAMES // 2)
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

    def test_optimizer_post_process_strip_with_branch(self):
        br_exch_plan_1 = ExchangePlan()
        br_exch_plan_1.append_child(StoragePlan(None, None))

        br_exch_plan_2 = ExchangePlan()
        br_exch_plan_2.append_child(StoragePlan(None, None))

        nest_plan = NestedLoopJoinPlan(None)
        nest_plan.append_child(br_exch_plan_1)
        nest_plan.append_child(br_exch_plan_2)

        proj_plan = ProjectPlan(None)
        proj_plan.append_child(nest_plan)

        root_exch_plan = ExchangePlan()
        root_exch_plan.append_child(proj_plan)

        plan = PlanGenerator().post_process(root_exch_plan)

        self.assertTrue(isinstance(plan, ProjectPlan))
        self.assertEqual(len(plan.children), 1)
        self.assertTrue(isinstance(plan.children[0], NestedLoopJoinPlan))
        self.assertEqual(len(nest_plan.children), 2)
        self.assertTrue(isinstance(nest_plan.children[0], StoragePlan))
        self.assertTrue(isinstance(nest_plan.children[1], StoragePlan))

    def test_optimizer_post_process_strip_without_branch(self):
        child_exch_plan = ExchangePlan()
        child_exch_plan.append_child(StoragePlan(None, None))

        proj_plan = ProjectPlan(None)
        proj_plan.append_child(child_exch_plan)

        root_exch_plan = ExchangePlan()
        root_exch_plan.append_child(proj_plan)

        plan = PlanGenerator().post_process(root_exch_plan)

        self.assertTrue(isinstance(plan, ExchangePlan))
        self.assertEqual(len(plan.children), 1)
        self.assertTrue(isinstance(plan.children[0], ProjectPlan))
        self.assertEqual(len(proj_plan.children), 1)
        self.assertTrue(isinstance(proj_plan.children[0], ExchangePlan))
        self.assertEqual(len(child_exch_plan.children), 1)
        self.assertTrue(isinstance(child_exch_plan.children[0], StoragePlan))

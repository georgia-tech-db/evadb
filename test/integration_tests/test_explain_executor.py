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
from test.util import create_sample_video, file_remove, load_udfs_for_testing

import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.rules.rules import (
    EmbedFilterIntoGet,
    LogicalInnerJoinCommutativity,
    XformLateralJoinToLinearFlow,
)
from eva.optimizer.rules.rules_manager import disable_rules
from eva.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


@pytest.mark.notparallel
class ExplainExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        video_file_path = create_sample_video(NUM_FRAMES)
        load_query = f"LOAD VIDEO '{video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(load_query)
        load_udfs_for_testing(mode="minimal")

    @classmethod
    def tearDownClass(cls):
        file_remove("dummy.avi")
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

    def test_explain_simple_select(self):
        ray_enabled = ConfigurationManager().get_value("experimental", "ray")
        select_query = "EXPLAIN SELECT id, data FROM MyVideo"
        batch = execute_query_fetch_all(select_query)
        expected_output = (
            """|__ ExchangePlan\n    |__ ProjectPlan\n        |__ SeqScanPlan\n            |__ ExchangePlan\n                |__ StoragePlan\n"""
            if ray_enabled
            else """|__ ProjectPlan\n    |__ SeqScanPlan\n        |__ StoragePlan\n"""
        )
        self.assertEqual(batch.frames[0][0], expected_output)

        with disable_rules([XformLateralJoinToLinearFlow()]) as rules_manager:
            custom_plan_generator = PlanGenerator(rules_manager)
            select_query = "EXPLAIN SELECT id, data FROM MyVideo JOIN LATERAL DummyObjectDetector(data) AS T ;"
            batch = execute_query_fetch_all(
                select_query, plan_generator=custom_plan_generator
            )
            expected_output = (
                """|__ ProjectPlan\n    |__ LateralJoinPlan\n        |__ SeqScanPlan\n            |__ StoragePlan\n        |__ FunctionScanPlan\n"""
                if ray_enabled
                else """|__ ProjectPlan\n    |__ LateralJoinPlan\n        |__ SeqScanPlan\n            |__ StoragePlan\n        |__ FunctionScanPlan\n"""
            )
            self.assertEqual(batch.frames[0][0], expected_output)

        # Disable more rules
        with disable_rules(
            [
                XformLateralJoinToLinearFlow(),
                EmbedFilterIntoGet(),
                LogicalInnerJoinCommutativity(),
            ]
        ) as rules_manager:
            custom_plan_generator = PlanGenerator(rules_manager)
            select_query = "EXPLAIN SELECT id, data FROM MyVideo JOIN LATERAL DummyObjectDetector(data) AS T ;"
            batch = execute_query_fetch_all(
                select_query, plan_generator=custom_plan_generator
            )
            expected_output = (
                """|__ ProjectPlan\n    |__ LateralJoinPlan\n        |__ SeqScanPlan\n            |__ StoragePlan\n        |__ FunctionScanPlan\n"""
                if ray_enabled
                else """|__ ProjectPlan\n    |__ LateralJoinPlan\n        |__ SeqScanPlan\n            |__ StoragePlan\n        |__ FunctionScanPlan\n"""
            )
            self.assertEqual(batch.frames[0][0], expected_output)

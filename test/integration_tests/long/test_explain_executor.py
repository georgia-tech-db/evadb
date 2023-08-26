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
from test.util import (
    create_sample_video,
    file_remove,
    get_evadb_for_testing,
    load_udfs_for_testing,
)

import pytest

from evadb.optimizer.plan_generator import PlanGenerator
from evadb.optimizer.rules.rules import (
    EmbedFilterIntoGet,
    LogicalInnerJoinCommutativity,
    XformLateralJoinToLinearFlow,
)
from evadb.optimizer.rules.rules_manager import RulesManager, disable_rules
from evadb.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


@pytest.mark.notparallel
class ExplainExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()
        video_file_path = create_sample_video(NUM_FRAMES)
        load_query = f"LOAD VIDEO '{video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(cls.evadb, load_query)
        load_udfs_for_testing(cls.evadb, mode="debug")

    @classmethod
    def tearDownClass(cls):
        file_remove("dummy.avi")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MyVideo;")

    def test_explain_simple_select(self):
        select_query = "EXPLAIN SELECT id, data FROM MyVideo"
        batch = execute_query_fetch_all(self.evadb, select_query)
        expected_output = (
            """|__ ProjectPlan\n    |__ SeqScanPlan\n        |__ StoragePlan\n"""
        )
        self.assertEqual(batch.frames[0][0], expected_output)
        rules_manager = RulesManager(self.evadb.config)
        with disable_rules(rules_manager, [XformLateralJoinToLinearFlow()]):
            custom_plan_generator = PlanGenerator(self.evadb, rules_manager)
            select_query = "EXPLAIN SELECT id, data FROM MyVideo JOIN LATERAL DummyObjectDetector(data) AS T ;"
            batch = execute_query_fetch_all(
                self.evadb, select_query, plan_generator=custom_plan_generator
            )
            expected_output = """|__ ProjectPlan\n    |__ LateralJoinPlan\n        |__ SeqScanPlan\n            |__ StoragePlan\n        |__ FunctionScanPlan\n"""
            self.assertEqual(batch.frames[0][0], expected_output)

        # Disable more rules
        rules_manager = RulesManager(self.evadb.config)
        with disable_rules(
            rules_manager,
            [
                XformLateralJoinToLinearFlow(),
                EmbedFilterIntoGet(),
                LogicalInnerJoinCommutativity(),
            ],
        ):
            custom_plan_generator = PlanGenerator(self.evadb, rules_manager)
            select_query = "EXPLAIN SELECT id, data FROM MyVideo JOIN LATERAL DummyObjectDetector(data) AS T ;"
            batch = execute_query_fetch_all(
                self.evadb, select_query, plan_generator=custom_plan_generator
            )
            expected_output = """|__ ProjectPlan\n    |__ LateralJoinPlan\n        |__ SeqScanPlan\n            |__ StoragePlan\n        |__ FunctionScanPlan\n"""
            self.assertEqual(batch.frames[0][0], expected_output)


if __name__ == "__main__":
    unittest.main()

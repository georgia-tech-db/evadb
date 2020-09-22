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

from src.optimizer.operators import LogicalProject, LogicalFilter, LogicalGet
from src.optimizer.generators.seq_scan_generator import ScanGenerator
from src.planner.seq_scan_plan import SeqScanPlan
from src.planner.storage_plan import StoragePlan
from src.planner.types import PlanOprType


class SequentialScanGeneratorTest(unittest.TestCase):
    def test_should_return_correct_plan_tree_for_input_logical_tree(self):
        logical_plan = LogicalProject([1, 2], [LogicalFilter("a", [LogicalGet(
            "video", 1)])])

        plan = ScanGenerator().build(logical_plan)
        self.assertTrue(isinstance(plan, SeqScanPlan))
        self.assertEqual("a", plan.predicate)
        self.assertEqual([1, 2], plan.columns)
        self.assertEqual(PlanOprType.STORAGE_PLAN, plan.children[0].opr_type)
        self.assertEqual(1, plan.children[0].video)

    def test_should_just_get_plan_with_storage_if_no_predicate_and_tlist(self):
        logical_plan = LogicalGet("video", 1)
        plan = ScanGenerator().build(logical_plan)
        self.assertTrue(isinstance(plan, StoragePlan))
        self.assertEqual(1, plan.video)

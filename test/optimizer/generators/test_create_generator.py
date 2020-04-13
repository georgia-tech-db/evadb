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
from src.optimizer.operators import LogicalCreate
from src.optimizer.plan_generator import PlanGenerator
from src.planner.create_plan import CreatePlan


class CreateGeneratorTest(unittest.TestCase):
    def test_should_return_correct_plan_tree_for_input_logical_tree(self):
        logical_plan = LogicalCreate("video", [1, 2], True)
        plan = PlanGenerator().build(logical_plan)
        self.assertIsInstance(plan, CreatePlan)
        self.assertEqual(plan.video_ref, 'video')
        self.assertEqual(plan.column_list, [1, 2])
        self.assertEqual(plan.if_not_exists, True)

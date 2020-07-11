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
from src.optimizer.operators import LogicalLoadData
from src.optimizer.plan_generator import PlanGenerator
from src.planner.load_data_plan import LoadDataPlan


class LoadDataGeneratorTest(unittest.TestCase):
    def test_should_return_correct_plan_tree_for_input_logical_tree(self):
        logical_plan = LogicalLoadData('metainfo', 'path')
        plan = PlanGenerator().build(logical_plan)
        self.assertIsInstance(plan, LoadDataPlan)
        self.assertEqual(plan.table_metainfo, 'metainfo')
        self.assertEqual(plan.file_path, 'path')
        
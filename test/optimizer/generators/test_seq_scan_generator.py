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


from src.expression.tuple_value_expression import TupleValueExpression
from src.optimizer.operators import (LogicalProject, LogicalGet, LogicalFilter,
                                     LogicalOrderBy, LogicalLimit)

from src.optimizer.generators.seq_scan_generator import ScanGenerator
from src.parser.types import ParserOrderBySortType
from src.planner.seq_scan_plan import SeqScanPlan
from src.planner.storage_plan import StoragePlan
from src.planner.orderby_plan import OrderByPlan
from src.planner.limit_plan import LimitPlan
from src.planner.types import PlanOprType
from src.expression.constant_value_expression import ConstantValueExpression


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

    def test_should_return_correct_plan_tree_for_orderby_logical_tree(self):
        # SELECT data, id FROM video ORDER BY data, id DESC;
        logical_plan = LogicalOrderBy(
            [(TupleValueExpression('data'), ParserOrderBySortType.ASC),
             (TupleValueExpression('id'), ParserOrderBySortType.DESC)])

        plan = ScanGenerator().build(logical_plan)

        self.assertTrue(isinstance(plan, OrderByPlan))
        self.assertEqual(TupleValueExpression('data'), plan.orderby_list[0][0])
        self.assertEqual(ParserOrderBySortType.ASC, plan.orderby_list[0][1])
        self.assertEqual(TupleValueExpression('id'), plan.orderby_list[1][0])
        self.assertEqual(ParserOrderBySortType.DESC, plan.orderby_list[1][1])

    def test_should_return_correct_plan_tree_for_limit_logical_tree(self):
        # SELECT data, id FROM video limit 5;
        logical_plan = LogicalLimit(ConstantValueExpression(5))

        plan = ScanGenerator().build(logical_plan)

        self.assertTrue(isinstance(plan, LimitPlan))
        self.assertTrue(isinstance(
            plan.limit_expression, ConstantValueExpression))
        self.assertEqual(plan.limit_value, 5)

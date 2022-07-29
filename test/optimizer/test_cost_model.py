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
from copy import copy

from mock import MagicMock

from eva.optimizer.group_expression import GroupExpression
from eva.optimizer.operators import Operator
from eva.optimizer.optimizer_context import OptimizerContext
from eva.optimizer.optimizer_tasks import OptimizeGroup
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.property import PropertyType


class CostModel(unittest.TestCase):
    def execute_task_stack(self, task_stack):
        while not task_stack.empty():
            task = task_stack.pop()
            task.execute()

    def test_should_select_cheap_plan(self):
        # mocking the cost model
        def side_effect_func(value):
            if value is grp_expr1:
                return 1
            elif value is grp_expr2:
                return 2

        cm = CostModel()
        cm.calculate_cost = MagicMock(side_effect=side_effect_func)
        opt_cxt = OptimizerContext(cm)

        grp_expr1 = GroupExpression(MagicMock())
        grp_expr1.opr.is_logical = lambda: False

        grp_expr2 = GroupExpression(MagicMock())
        grp_expr2.opr.is_logical = lambda: False
        opt_cxt.memo.add_group_expr(grp_expr1)
        opt_cxt.memo.add_group_expr(grp_expr2, grp_expr1.group_id)
        grp = opt_cxt.memo.get_group_by_id(grp_expr1.group_id)
        opt_cxt.task_stack.push(OptimizeGroup(grp, opt_cxt))
        self.execute_task_stack(opt_cxt.task_stack)
        plan = PlanGenerator().build_optimal_physical_plan(grp_expr1.group_id, opt_cxt)
        self.assertEqual(plan, grp_expr1.opr)
        self.assertEqual(grp.get_best_expr_cost(PropertyType.DEFAULT), 1)

    def test_should_select_cheap_plan_with_tree(self):
        # mocking the cost model
        def side_effect_func(value):
            cost = dict(
                {
                    grp_expr00: 1,
                    grp_expr01: 2,
                    grp_expr10: 4,
                    grp_expr11: 3,
                    grp_expr20: 5,
                }
            )
            return cost[value]

        cm = CostModel()
        cm.calculate_cost = MagicMock(side_effect=side_effect_func)
        opt_cxt = OptimizerContext(cm)

        # group 0
        grp_expr00 = GroupExpression(Operator(MagicMock()))
        grp_expr00.opr.is_logical = lambda: False
        grp_expr01 = GroupExpression(Operator(MagicMock()))
        grp_expr01.opr.is_logical = lambda: False
        opt_cxt.memo.add_group_expr(grp_expr00)
        opt_cxt.memo.add_group_expr(grp_expr01, grp_expr00.group_id)

        # group 1
        grp_expr10 = GroupExpression(Operator(MagicMock()))
        grp_expr10.opr.is_logical = lambda: False
        opt_cxt.memo.add_group_expr(grp_expr10)
        grp_expr11 = GroupExpression(Operator(MagicMock()))
        grp_expr11.opr.is_logical = lambda: False
        opt_cxt.memo.add_group_expr(grp_expr11, grp_expr10.group_id)

        # group 2
        grp_expr20 = GroupExpression(Operator(MagicMock()))
        grp_expr20.opr.is_logical = lambda: False
        opt_cxt.memo.add_group_expr(grp_expr20)
        grp = opt_cxt.memo.get_group_by_id(grp_expr20.group_id)

        # tree:  2->1->0
        grp_expr10.children = [grp_expr01.group_id]
        grp_expr11.children = [grp_expr01.group_id]
        grp_expr20.children = [grp_expr10.group_id]

        opt_cxt.task_stack.push(OptimizeGroup(grp, opt_cxt))
        self.execute_task_stack(opt_cxt.task_stack)
        plan = PlanGenerator().build_optimal_physical_plan(grp_expr20.group_id, opt_cxt)
        subplan = copy(grp_expr11.opr)
        subplan.children = [copy(grp_expr01.opr)]
        expected_plan = copy(grp_expr20.opr)
        expected_plan.children = [subplan]

        self.assertEqual(plan, expected_plan)
        self.assertEqual(grp.get_best_expr_cost(PropertyType.DEFAULT), 9)

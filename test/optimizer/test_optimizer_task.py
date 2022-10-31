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
from unittest.mock import patch

from mock import MagicMock

from eva.optimizer.cost_model import CostModel
from eva.optimizer.operators import (
    LogicalFilter,
    LogicalGet,
    LogicalProject,
    LogicalQueryDerivedGet,
)
from eva.optimizer.optimizer_context import OptimizerContext
from eva.optimizer.optimizer_tasks import BottomUpRewrite, OptimizeGroup, TopDownRewrite
from eva.optimizer.property import PropertyType
from eva.optimizer.rules.rules_manager import RulesManager
from eva.planner.predicate_plan import PredicatePlan
from eva.planner.project_plan import ProjectPlan
from eva.planner.seq_scan_plan import SeqScanPlan


class TestOptimizerTask(unittest.TestCase):
    def execute_task_stack(self, task_stack):
        while not task_stack.empty():
            task = task_stack.pop()
            task.execute()

    def top_down_rewrite(self, opr):
        opt_cxt = OptimizerContext(CostModel())
        grp_expr = opt_cxt.add_opr_to_group(opr)
        root_grp_id = grp_expr.group_id
        opt_cxt.task_stack.push(
            TopDownRewrite(grp_expr, RulesManager().rewrite_rules, opt_cxt)
        )
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def bottom_up_rewrite(self, root_grp_id, opt_cxt):
        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]
        opt_cxt.task_stack.push(
            BottomUpRewrite(grp_expr, RulesManager().rewrite_rules, opt_cxt)
        )
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def implement_group(self, root_grp_id, opt_cxt):
        grp = opt_cxt.memo.groups[root_grp_id]
        opt_cxt.task_stack.push(OptimizeGroup(grp, opt_cxt))
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def test_simple_top_down_rewrite(self):
        predicate = MagicMock()
        video = MagicMock()
        with patch("eva.optimizer.rules.rules.extract_pushdown_predicate") as mock:
            mock.return_value = (predicate, None)
            child_opr = LogicalGet(video, MagicMock(), MagicMock())
            root_opr = LogicalFilter(predicate, [child_opr])

            opt_cxt, root_grp_id = self.top_down_rewrite(root_opr)

            grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]

            self.assertEqual(type(grp_expr.opr), LogicalGet)
            self.assertEqual(grp_expr.opr.predicate, predicate)
            self.assertEqual(grp_expr.opr.children, [])

    def test_nested_top_down_rewrite(self):
        child_predicate = MagicMock()
        root_predicate = MagicMock()
        with patch("eva.optimizer.rules.rules.extract_pushdown_predicate") as mock:
            mock.side_effect = [
                (root_predicate, None),
                (root_predicate, None),
                (child_predicate, None),
                (child_predicate, None),
            ]
            child_get_opr = LogicalGet(MagicMock(), MagicMock(), MagicMock())
            child_filter_opr = LogicalFilter(child_predicate, [child_get_opr])
            child_project_opr = LogicalProject([MagicMock()], [child_filter_opr])
            root_derived_get_opr = LogicalQueryDerivedGet(
                MagicMock(), children=[child_project_opr]
            )
            root_filter_opr = LogicalFilter(root_predicate, [root_derived_get_opr])
            root_project_opr = LogicalProject([MagicMock()], [root_filter_opr])

            opt_cxt, root_grp_id = self.top_down_rewrite(root_project_opr)

            expected_expr_order = [
                LogicalProject,
                LogicalFilter,
                LogicalQueryDerivedGet,
                LogicalProject,
                LogicalGet,
            ]
            curr_grp_id = root_grp_id
            idx = 0
            while True:
                grp_expr = opt_cxt.memo.groups[curr_grp_id].logical_exprs[0]
                self.assertEqual(type(grp_expr.opr), expected_expr_order[idx])
                idx += 1
                if idx == len(expected_expr_order):
                    break
                curr_grp_id = grp_expr.children[0]

    def test_nested_bottom_up_rewrite(self):
        child_predicate = MagicMock()
        root_predicate = MagicMock()
        with patch("eva.optimizer.rules.rules.extract_pushdown_predicate") as mock:
            mock.side_effect = [
                (root_predicate, None),
                (root_predicate, None),
                (child_predicate, None),
                (child_predicate, None),
            ]

            child_get_opr = LogicalGet(MagicMock(), MagicMock(), MagicMock())
            child_filter_opr = LogicalFilter(child_predicate, [child_get_opr])
            child_project_opr = LogicalProject([MagicMock()], [child_filter_opr])
            root_derived_get_opr = LogicalQueryDerivedGet(
                MagicMock(), children=[child_project_opr]
            )
            root_filter_opr = LogicalFilter(root_predicate, [root_derived_get_opr])
            root_project_opr = LogicalProject([MagicMock()], children=[root_filter_opr])

            opt_cxt, root_grp_id = self.top_down_rewrite(root_project_opr)
            opt_cxt, root_grp_id = self.bottom_up_rewrite(root_grp_id, opt_cxt)

            expected_expr_order = [
                LogicalProject,
                LogicalFilter,
                LogicalQueryDerivedGet,
                LogicalGet,
            ]
            curr_grp_id = root_grp_id
            idx = 0
            while True:
                grp_expr = opt_cxt.memo.groups[curr_grp_id].logical_exprs[0]
                self.assertEqual(type(grp_expr.opr), expected_expr_order[idx])
                idx += 1
                if idx == len(expected_expr_order):
                    break
                curr_grp_id = grp_expr.children[0]

    def test_simple_implementation(self):
        predicate = MagicMock()
        child_opr = LogicalGet(MagicMock(), MagicMock(), MagicMock())
        root_opr = LogicalFilter(predicate, [child_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_opr)
        opt_cxt, root_grp_id = self.bottom_up_rewrite(root_grp_id, opt_cxt)
        opt_cxt, root_grp_id = self.implement_group(root_grp_id, opt_cxt)

        root_grp = opt_cxt.memo.groups[root_grp_id]
        best_root_grp_expr = root_grp.get_best_expr(PropertyType.DEFAULT)

        self.assertEqual(type(best_root_grp_expr.opr), PredicatePlan)

    def test_nested_implementation(self):
        child_predicate = MagicMock()
        root_predicate = MagicMock()
        with patch("eva.optimizer.rules.rules.extract_pushdown_predicate") as mock:
            mock.side_effect = [
                (child_predicate, None),
                (root_predicate, None),
            ]

            child_get_opr = LogicalGet(MagicMock(), MagicMock(), MagicMock())
            child_filter_opr = LogicalFilter(child_predicate, children=[child_get_opr])
            child_project_opr = LogicalProject(
                [MagicMock()], children=[child_filter_opr]
            )
            root_derived_get_opr = LogicalQueryDerivedGet(
                MagicMock(), children=[child_project_opr]
            )
            root_filter_opr = LogicalFilter(
                root_predicate, children=[root_derived_get_opr]
            )
            root_project_opr = LogicalProject([MagicMock()], children=[root_filter_opr])

            opt_cxt, root_grp_id = self.top_down_rewrite(root_project_opr)
            opt_cxt, root_grp_id = self.bottom_up_rewrite(root_grp_id, opt_cxt)
            opt_cxt, root_grp_id = self.implement_group(root_grp_id, opt_cxt)

            expected_expr_order = [
                ProjectPlan,
                PredicatePlan,
                SeqScanPlan,
                SeqScanPlan,
            ]
            curr_grp_id = root_grp_id
            idx = 0
            while True:
                root_grp = opt_cxt.memo.groups[curr_grp_id]
                best_root_grp_expr = root_grp.get_best_expr(PropertyType.DEFAULT)
                self.assertEqual(type(best_root_grp_expr.opr), expected_expr_order[idx])
                idx += 1
                if idx == len(expected_expr_order):
                    break
                curr_grp_id = best_root_grp_expr.children[0]

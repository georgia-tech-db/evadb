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
from unittest.mock import patch

from mock import MagicMock

from evadb.optimizer.cost_model import CostModel
from evadb.optimizer.operators import (
    LogicalFilter,
    LogicalGet,
    LogicalProject,
    LogicalQueryDerivedGet,
)
from evadb.optimizer.optimizer_context import OptimizerContext
from evadb.optimizer.optimizer_tasks import (
    BottomUpRewrite,
    OptimizeGroup,
    OptimizerTask,
    TopDownRewrite,
)
from evadb.optimizer.property import PropertyType
from evadb.optimizer.rules.rules_manager import RulesManager
from evadb.plan_nodes.predicate_plan import PredicatePlan
from evadb.plan_nodes.project_plan import ProjectPlan
from evadb.plan_nodes.seq_scan_plan import SeqScanPlan


class TestOptimizerTask(unittest.TestCase):
    def execute_task_stack(self, task_stack):
        while not task_stack.empty():
            task = task_stack.pop()
            task.execute()

    def test_abstract_optimizer_task(self):
        task = OptimizerTask(MagicMock(), MagicMock())

        with self.assertRaises(NotImplementedError):
            task.execute()

    def top_down_rewrite(self, opr):
        opt_cxt = OptimizerContext(MagicMock(), CostModel(), RulesManager(MagicMock()))
        grp_expr = opt_cxt.add_opr_to_group(opr)
        root_grp_id = grp_expr.group_id
        opt_cxt.task_stack.push(
            TopDownRewrite(
                grp_expr, RulesManager(MagicMock()).stage_one_rewrite_rules, opt_cxt
            )
        )
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def bottom_up_rewrite(self, root_grp_id, opt_cxt):
        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]
        opt_cxt.task_stack.push(
            BottomUpRewrite(
                grp_expr, RulesManager(MagicMock()).stage_two_rewrite_rules, opt_cxt
            )
        )
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def implement_group(self, root_grp_id, opt_cxt):
        grp = opt_cxt.memo.groups[root_grp_id]
        opt_cxt.task_stack.push(OptimizeGroup(grp, opt_cxt))
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

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
        with patch("evadb.optimizer.rules.rules.extract_pushdown_predicate") as mock:
            with patch("evadb.optimizer.rules.rules.is_video_table") as mock_vid:
                mock_vid.return_value = True
                mock.side_effect = [
                    (child_predicate, None),
                    (root_predicate, None),
                ]

                child_get_opr = LogicalGet(MagicMock(), MagicMock(), MagicMock())
                child_filter_opr = LogicalFilter(
                    child_predicate, children=[child_get_opr]
                )
                child_project_opr = LogicalProject(
                    [MagicMock()], children=[child_filter_opr]
                )
                root_derived_get_opr = LogicalQueryDerivedGet(
                    MagicMock(), children=[child_project_opr]
                )
                root_filter_opr = LogicalFilter(
                    root_predicate, children=[root_derived_get_opr]
                )
                root_project_opr = LogicalProject(
                    [MagicMock()], children=[root_filter_opr]
                )

                opt_cxt, root_grp_id = self.top_down_rewrite(root_project_opr)
                opt_cxt, root_grp_id = self.bottom_up_rewrite(root_grp_id, opt_cxt)
                opt_cxt, root_grp_id = self.implement_group(root_grp_id, opt_cxt)

                expected_expr_order = [
                    ProjectPlan,
                    PredicatePlan,
                    SeqScanPlan,
                    ProjectPlan,
                    SeqScanPlan,
                ]
                curr_grp_id = root_grp_id
                idx = 0
                while True:
                    root_grp = opt_cxt.memo.groups[curr_grp_id]
                    best_root_grp_expr = root_grp.get_best_expr(PropertyType.DEFAULT)
                    self.assertEqual(
                        type(best_root_grp_expr.opr), expected_expr_order[idx]
                    )
                    idx += 1
                    if idx == len(expected_expr_order):
                        break
                    curr_grp_id = best_root_grp_expr.children[0]

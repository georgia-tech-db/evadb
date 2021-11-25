import unittest

from mock import MagicMock

from eva.optimizer.optimizer_tasks import (
    TopDownRewrite, BottomUpRewrite, OptimizeGroup)
from eva.optimizer.optimizer_context import OptimizerContext
from eva.optimizer.operators import (
    LogicalGet, LogicalFilter, LogicalProject, LogicalQueryDerivedGet)
from eva.optimizer.property import PropertyType
from eva.planner.seq_scan_plan import SeqScanPlan


class TestOptimizerTask(unittest.TestCase):
    def execute_task_stack(self, task_stack):
        while not task_stack.empty():
            task = task_stack.pop()
            task.execute()

    def top_down_rewrite(self, opr):
        opt_cxt = OptimizerContext()
        grp_expr = opt_cxt.xform_opr_to_group_expr(
            opr,
            copy_opr=False
        )
        root_grp_id = grp_expr.group_id
        opt_cxt.task_stack.push(TopDownRewrite(grp_expr, opt_cxt))
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def bottom_up_rewrite(self, root_grp_id, opt_cxt):
        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]
        opt_cxt.task_stack.push(BottomUpRewrite(grp_expr, opt_cxt))
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def implement_group(self, root_grp_id, opt_cxt):
        opt_cxt.task_stack.push(OptimizeGroup(root_grp_id, opt_cxt))
        self.execute_task_stack(opt_cxt.task_stack)
        return opt_cxt, root_grp_id

    def test_simple_top_down_rewrite(self):
        predicate = MagicMock()
        child_opr = LogicalGet(MagicMock(), MagicMock())
        root_opr = LogicalFilter(predicate, [child_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_opr)

        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]

        self.assertEqual(type(grp_expr.opr), LogicalGet)
        self.assertEqual(grp_expr.opr.predicate, predicate)
        self.assertEqual(grp_expr.opr.children, [])

    def test_nested_top_down_rewrite(self):
        child_predicate = MagicMock()
        root_predicate = MagicMock()

        child_get_opr = LogicalGet(MagicMock(), MagicMock())
        child_filter_opr = LogicalFilter(child_predicate, [child_get_opr])
        child_project_opr = LogicalProject(MagicMock(), [child_filter_opr])
        root_derived_get_opr = LogicalQueryDerivedGet([child_project_opr])
        root_filter_opr = LogicalFilter(root_predicate, [root_derived_get_opr])
        root_project_opr = LogicalProject(MagicMock(), [root_filter_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_project_opr)

        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]

        # rewrite happens in a way that new expression is
        # inserted in a new group
        self.assertEqual(type(grp_expr.opr), LogicalProject)
        self.assertEqual(len(grp_expr.opr.children), 1)

        test_child_opr = grp_expr.opr.children[0]
        self.assertEqual(type(test_child_opr), LogicalFilter)
        self.assertEqual(len(test_child_opr.children), 1)
        self.assertEqual(test_child_opr.predicate, root_predicate)

        test_child_opr = test_child_opr.children[0]
        self.assertEqual(type(test_child_opr), LogicalQueryDerivedGet)
        self.assertEqual(len(test_child_opr.children), 1)

        test_child_opr = test_child_opr.children[0]
        self.assertEqual(type(test_child_opr), LogicalProject)
        self.assertEqual(len(test_child_opr.children), 1)

        test_child_opr = test_child_opr.children[0]
        self.assertEqual(type(test_child_opr), LogicalGet)
        self.assertEqual(test_child_opr.predicate, child_predicate)

    def test_nested_bottom_up_rewrite(self):
        child_predicate = MagicMock()
        root_predicate = MagicMock()

        child_get_opr = LogicalGet(MagicMock(), MagicMock())
        child_filter_opr = LogicalFilter(child_predicate, [child_get_opr])
        child_project_opr = LogicalProject(MagicMock(), [child_filter_opr])
        root_derived_get_opr = LogicalQueryDerivedGet([child_project_opr])
        root_filter_opr = LogicalFilter(root_predicate, [root_derived_get_opr])
        root_project_opr = LogicalProject(MagicMock(), [root_filter_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_project_opr)
        opt_cxt, root_grp_id = self.bottom_up_rewrite(root_grp_id, opt_cxt)

        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]

        self.assertEqual(type(grp_expr.opr), LogicalQueryDerivedGet)
        self.assertEqual(len(grp_expr.opr.children), 1)
        self.assertEqual(grp_expr.opr.predicate, root_predicate)

        test_child_opr = grp_expr.opr.children[0]
        self.assertEqual(type(test_child_opr), LogicalGet)
        self.assertEqual(test_child_opr.predicate, child_predicate)

    def test_simple_implementation(self):
        predicate = MagicMock()
        child_opr = LogicalGet(MagicMock(), MagicMock())
        root_opr = LogicalFilter(predicate, [child_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_opr)
        opt_cxt, root_grp_id = self.bottom_up_rewrite(root_grp_id, opt_cxt)
        opt_cxt, root_grp_id = self.implement_group(root_grp_id, opt_cxt)

        root_grp = opt_cxt.memo.groups[root_grp_id]
        best_root_grp_expr = root_grp.get_best_expr(PropertyType.DEFAULT)

        self.assertEqual(type(best_root_grp_expr.opr), SeqScanPlan)
        self.assertEqual(best_root_grp_expr.opr.predicate, predicate)

    def test_nested_implementation(self):
        child_predicate = MagicMock()
        root_predicate = MagicMock()

        child_get_opr = LogicalGet(MagicMock(), MagicMock())
        child_filter_opr = LogicalFilter(child_predicate, [child_get_opr])
        child_project_opr = LogicalProject(MagicMock(), [child_filter_opr])
        root_derived_get_opr = LogicalQueryDerivedGet([child_project_opr])
        root_filter_opr = LogicalFilter(root_predicate, [root_derived_get_opr])
        root_project_opr = LogicalProject(MagicMock(), [root_filter_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_project_opr)
        opt_cxt, root_grp_id = self.bottom_up_rewrite(root_grp_id, opt_cxt)
        opt_cxt, root_grp_id = self.implement_group(root_grp_id, opt_cxt)

        root_grp = opt_cxt.memo.groups[root_grp_id]
        best_root_grp_expr = root_grp.get_best_expr(PropertyType.DEFAULT)

        root_opr = best_root_grp_expr.opr
        self.assertEqual(type(root_opr), SeqScanPlan)
        self.assertEqual(root_opr.predicate, root_predicate)

        child_grp_id = best_root_grp_expr.children[0]
        child_grp = opt_cxt.memo.groups[child_grp_id]
        best_child_grp_expr = child_grp.get_best_expr(PropertyType.DEFAULT)
        child_opr = best_child_grp_expr.opr
        self.assertEqual(type(child_opr), SeqScanPlan)
        self.assertEqual(child_opr.predicate, child_predicate)

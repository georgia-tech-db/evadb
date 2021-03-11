import unittest

from mock import MagicMock

from src.optimizer.optimizer_tasks import TopDownRewrite
from src.optimizer.optimizer_context import OptimizerContext
from src.optimizer.operators import (LogicalGet, LogicalFilter)


class TestOptimizerTask(unittest.TestCase):
    def top_down_rewrite(self, opr):
        opt_cxt = OptimizerContext()
        grp_expr = opt_cxt.xform_opr_to_group_expr(
            opr,
            copy_opr=False
        )
        root_grp_id = grp_expr.group_id
        opt_cxt.task_stack.push(TopDownRewrite(grp_expr, opt_cxt))

        while not opt_cxt.task_stack.empty():
            task = opt_cxt.task_stack.pop()
            task.execute()

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
        child1_predicate = MagicMock()
        child2_predicate = MagicMock()
        root_predicate = MagicMock()

        child1_child_opr = LogicalGet(MagicMock(), MagicMock())
        child2_child_opr = LogicalGet(MagicMock(), MagicMock())
        child1_opr = LogicalFilter(child1_predicate, [child1_child_opr])
        child2_opr = LogicalFilter(child2_predicate, [child2_child_opr])
        root_opr = LogicalFilter(root_predicate, [child1_opr, child2_opr])

        opt_cxt, root_grp_id = self.top_down_rewrite(root_opr)

        grp_expr = opt_cxt.memo.groups[root_grp_id].logical_exprs[0]

        # rewrite happens in a way that new expression is
        # inserted in a new group
        self.assertEqual(type(grp_expr.opr), LogicalFilter)
        self.assertEqual(len(grp_expr.opr.children), 2)

        child1_opr = grp_expr.opr.children[0]
        self.assertEqual(type(child1_opr), LogicalFilter)
        self.assertEqual(child1_opr.predicate, child1_predicate)

        child2_opr = grp_expr.opr.children[1]
        self.assertEqual(type(child2_opr), LogicalFilter)
        self.assertEqual(child2_opr.predicate, child2_predicate)

        # check expression children
        for child_id in grp_expr.children:
            expr = opt_cxt.memo.groups[child_id].logical_exprs[0]

            # filter should have been already embedded in get
            self.assertEqual(type(expr.opr), LogicalGet)

            if child_id == 1:
                self.assertEqual(expr.opr.predicate, child1_predicate)
            else:
                self.assertEqual(expr.opr.predicate, child2_predicate)

import unittest

from mock import patch, MagicMock

from eva.optimizer.optimizer_context import OptimizerContext
from eva.optimizer.group_expression import GroupExpression
from eva.optimizer.group import INVALID_GROUP_ID


class TestOptimizerContext(unittest.TestCase):
    def test_add_root(self):
        fake_opr = MagicMock()
        fake_opr.children = []

        opt_ctxt = OptimizerContext()
        opt_ctxt.xform_opr_to_group_expr(fake_opr)
        self.assertEqual(len(opt_ctxt.memo.group_exprs), 1)

    @unittest.skip('Forcing ID will only happen when memo exists group')
    def test_add_root_guaranteed_group_id(self):
        fake_opr = MagicMock()
        fake_opr.children = []

        opt_ctxt = OptimizerContext()
        opt_ctxt.xform_opr_to_group_expr(fake_opr, 0, True)
        self.assertEqual(opt_ctxt.memo.get_group_id(fake_opr), 0)

    @patch('eva.optimizer.operators.Operator')
    @patch('eva.optimizer.operators.Operator')
    @patch('eva.optimizer.operators.Operator')
    @patch('eva.optimizer.operators.Operator')
    def test_opr_to_group_expr(self,
                               child1_opr,
                               child2_opr,
                               child3_opr,
                               root_opr):
        child1_opr.children = []
        child1_expr = GroupExpression(child1_opr, INVALID_GROUP_ID, [])

        child2_opr.children = []
        child2_expr = GroupExpression(child2_opr, INVALID_GROUP_ID, [])

        child3_opr.children = []
        child3_expr = GroupExpression(child3_opr, INVALID_GROUP_ID, [])

        root_expr = GroupExpression(root_opr,
                                    INVALID_GROUP_ID,
                                    [0, 1, 2])
        root_opr.children = [child1_opr, child2_opr, child3_opr]

        opt_ctxt = OptimizerContext()
        opt_ctxt.xform_opr_to_group_expr(
            root_opr, is_root=True, copy_opr=False)
        self.assertEqual(len(opt_ctxt.memo.group_exprs), 4)
        self.assertEqual(opt_ctxt.memo.get_group_id(child3_expr), 2)
        self.assertEqual(opt_ctxt.memo.get_group_id(child2_expr), 1)
        self.assertEqual(opt_ctxt.memo.get_group_id(child1_expr), 0)
        self.assertEqual(opt_ctxt.memo.get_group_id(root_expr), 3)

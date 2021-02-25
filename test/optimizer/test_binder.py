import unittest
import copy

from mock import MagicMock

from src.optimizer.binder import Binder
from src.optimizer.group_expression import GroupExpression
from src.optimizer.optimizer_context import OptimizerContext
from src.optimizer.operators import (OperatorType, LogicalFilter, LogicalGet)
from src.optimizer.rules.pattern import Pattern


class TestBinder(unittest.TestCase):
    def helper_pre_order_match(self, cur_opr, res_opr):
        self.assertEqual(cur_opr.opr_type, res_opr.opr_type)
        self.assertEqual(len(cur_opr.children), len(res_opr.children))

        for i, child_opr in enumerate(cur_opr.children):
            self.helper_pre_order_match(child_opr, res_opr.children[i])

    def test_simple_binder_match(self):
        child1_opr = LogicalGet(MagicMock(), MagicMock())
        child2_opr = LogicalGet(MagicMock(), MagicMock())
        root_opr = LogicalFilter(MagicMock(), [child1_opr, child2_opr])

        child1_ptn = Pattern(OperatorType.LOGICALGET)
        child2_ptn = Pattern(OperatorType.LOGICALGET)
        root_ptn = Pattern(OperatorType.LOGICALFILTER)
        root_ptn.append_child(child1_ptn)
        root_ptn.append_child(child2_ptn)

        opt_ctxt = OptimizerContext()
        root_grp_expr = opt_ctxt.xform_opr_to_group_expr(
            root_opr, is_root=True)

        binder = Binder(root_grp_expr, root_ptn, opt_ctxt.memo)

        for match in iter(binder):
            self.helper_pre_order_match(root_opr, match)

    def test_nested_binder_match(self):
        sub_child_opr = LogicalGet(MagicMock(), MagicMock())
        sub_root_opr = LogicalFilter(MagicMock(), [sub_child_opr])

        child_opr = LogicalGet(MagicMock(), MagicMock())
        root_opr = LogicalFilter(MagicMock(), [child_opr])

        # copy for binder to operate on
        sub_child_opr_cpy = LogicalGet(MagicMock(), MagicMock())
        sub_root_opr_cpy = LogicalFilter(MagicMock(), [sub_child_opr_cpy])

        child_opr_cpy = LogicalGet(MagicMock(), MagicMock())
        root_opr_cpy = LogicalFilter(MagicMock(), [child_opr_cpy])
        root_opr_cpy.append_child(sub_root_opr_cpy)

        child_ptn = Pattern(OperatorType.LOGICALGET)
        root_ptn = Pattern(OperatorType.LOGICALFILTER)
        root_ptn.append_child(child_ptn)

        opt_ctxt = OptimizerContext()
        root_grp_expr = opt_ctxt.xform_opr_to_group_expr(
            root_opr_cpy, is_root=True)

        binder = Binder(root_grp_expr, root_ptn, opt_ctxt.memo)

        i = 0
        for match in iter(binder):
            if i == 0:
                self.helper_pre_order_match(root_opr, match)
            else:
                self.helper_pre_order_match(sub_root_opr, match)
            i += 1
        self.assertEqual(i, 2)

import unittest

from mock import MagicMock

from eva.optimizer.binder import Binder
from eva.optimizer.optimizer_context import OptimizerContext
from eva.optimizer.operators import (
    OperatorType, LogicalFilter, LogicalGet, Dummy)
from eva.optimizer.rules.pattern import Pattern


class TestBinder(unittest.TestCase):
    def helper_pre_order_match(self, cur_opr, res_opr):
        self.assertEqual(cur_opr.opr_type, res_opr.opr_type)
        self.assertEqual(len(cur_opr.children), len(res_opr.children))

        for i, child_opr in enumerate(cur_opr.children):
            self.helper_pre_order_match(child_opr, res_opr.children[i])

    def test_simple_binder_match(self):
        """
        Opr Tree:
                         LogicalFilter
                         /           \
                  LogicalGet      LogicalGet

        Pattern:
                         LogicalFilter
                         /           \
                  LogicalGet      LogicalGet
        """
        child1_opr = LogicalGet(MagicMock(), MagicMock())
        child2_opr = LogicalGet(MagicMock(), MagicMock())
        root_opr = LogicalFilter(MagicMock(), [child1_opr, child2_opr])

        child1_ptn = Pattern(OperatorType.LOGICALGET)
        child2_ptn = Pattern(OperatorType.LOGICALGET)
        root_ptn = Pattern(OperatorType.LOGICALFILTER)
        root_ptn.append_child(child1_ptn)
        root_ptn.append_child(child2_ptn)

        opt_ctxt = OptimizerContext()
        root_grp_expr = opt_ctxt.add_opr_to_group(
            root_opr)

        binder = Binder(root_grp_expr, root_ptn, opt_ctxt.memo)

        for match in iter(binder):
            self.helper_pre_order_match(root_opr, match)

    def test_nested_binder_match(self):
        """
        Opr Tree:
                         LogicalFilter
                         /           \
                  LogicalGet      LogicalFilter
                                  /           \
                            LogicalGet       LogicalGet

        Pattern:
                         LogicalFilter
                         /           \
                  LogicalGet      Dummy
        """

        sub_child_opr = LogicalGet(MagicMock(), MagicMock())
        sub_child_opr_2 = LogicalGet(MagicMock(), MagicMock())
        sub_root_opr = LogicalFilter(
            MagicMock(), [sub_child_opr, sub_child_opr_2])

        child_opr = LogicalGet(MagicMock(), MagicMock())
        root_opr = LogicalFilter(
            MagicMock(), [child_opr, sub_root_opr])

        child_ptn = Pattern(OperatorType.LOGICALGET)
        root_ptn = Pattern(OperatorType.LOGICALFILTER)
        root_ptn.append_child(child_ptn)
        root_ptn.append_child(Pattern(OperatorType.DUMMY))

        opt_ctxt = OptimizerContext()
        root_grp_expr = opt_ctxt.add_opr_to_group(
            root_opr)
        binder = Binder(root_grp_expr, root_ptn, opt_ctxt.memo)
        expected_match = root_opr
        expected_match.append_child(child_opr)
        expected_match.append_child(Dummy(2))
        for match in iter(binder):
            self.helper_pre_order_match(expected_match, match)

        opt_ctxt = OptimizerContext()
        sub_root_grp_expr = opt_ctxt.add_opr_to_group(
            sub_root_opr)
        expected_match = sub_root_opr
        expected_match.append_child(sub_child_opr)
        expected_match.append_child(Dummy(1))
        binder = Binder(sub_root_grp_expr, root_ptn, opt_ctxt.memo)
        for match in iter(binder):
            self.helper_pre_order_match(sub_root_opr, match)

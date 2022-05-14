import unittest

from mock import MagicMock
from eva.optimizer.cost_model import CostModel

from eva.optimizer.optimizer_context import OptimizerContext


class TestOptimizerContext(unittest.TestCase):
    def test_add_root(self):
        fake_opr = MagicMock()
        fake_opr.children = []

        opt_ctxt = OptimizerContext(CostModel())
        opt_ctxt.add_opr_to_group(fake_opr)
        self.assertEqual(len(opt_ctxt.memo.group_exprs), 1)

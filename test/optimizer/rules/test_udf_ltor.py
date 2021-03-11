import unittest

from mock import MagicMock

# from src.optimizer.rules.rules import UdfLTOR
from src.optimizer.operators import LogicalFilter, Dummy
from src.expression.abstract_expression import ExpressionType
from src.expression.function_expression import FunctionExpression
from src.expression.logical_expression import LogicalExpression


class TestUdfLTOR(unittest.TestCase):
    @unittest.skip("LtoR rule does not work without logical shortcircuiting")
    def test_simple_udf_ltor(self):
        rule = UdfLTOR()

        child1_expr = FunctionExpression(MagicMock())
        child2_expr = LogicalExpression(
            ExpressionType.LOGICAL_AND, MagicMock(), MagicMock())
        root_expr = LogicalExpression(
            ExpressionType.LOGICAL_AND, child1_expr, child2_expr)

        logi_filter = LogicalFilter(root_expr, [Dummy()])
        rule.apply(logi_filter, MagicMock())

        self.assertEqual(root_expr.children[0], child2_expr)

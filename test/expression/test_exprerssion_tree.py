import unittest

import numpy as np

from src.expression.abstract_expression import ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.function_expression import FunctionExpression
from src.models import Prediction, FrameBatch, Frame


class ExpressionEvaluationTest(unittest.TestCase):
    def test_func_expr_with_cmpr_and_const_expr_should_work(self):
        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(1, 2 * np.ones((1, 1)), None)
        outcome_1 = Prediction(frame_1, ["car", "bus"], [0.5, 0.6])
        outcome_2 = Prediction(frame_1, ["bus"], [0.6])

        func = FunctionExpression(lambda x: [outcome_1, outcome_2])
        value_expr = ConstantValueExpression("car")
        expression_tree = ComparisonExpression(ExpressionType.COMPARE_EQUAL,
                                               func,
                                               value_expr)

        batch = FrameBatch(frames=[
            frame_1, frame_2
        ], info=None)

        self.assertEqual([True, False], expression_tree.evaluate(batch))

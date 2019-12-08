import unittest
import numpy as np

from src.expression.abstract_expression import ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.logical_expression import LogicalExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame


class LogicalExpressionsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_logical_and(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        comparison_expression_left = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL,
            tpl_exp,
            const_exp
        )
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)
        comparison_expression_right = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
            tpl_exp,
            const_exp
        )
        logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_AND,
            comparison_expression_left,
            comparison_expression_right
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)

        expected_value = [[False], [False], [False]]
        output_value  = logical_expr.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

    def test_logical_or(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        comparison_expression_left = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL,
            tpl_exp,
            const_exp
        )
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)
        comparison_expression_right = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
            tpl_exp,
            const_exp
        )
        logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_OR,
            comparison_expression_left,
            comparison_expression_right
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)

        expected_value = [[True], [True], [True]]
        output_value  = logical_expr.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

    def test_logical_not(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        comparison_expression_right = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
            tpl_exp,
            const_exp
        )
        logical_expr = LogicalExpression(
            ExpressionType.LOGICAL_NOT,
            None,
            comparison_expression_right
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)

        expected_value = [True, False, False]
        output_value  = logical_expr.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

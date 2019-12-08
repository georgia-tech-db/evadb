import unittest
import numpy as np

from src.expression.abstract_expression import ExpressionType
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.expression.arithmetic_expression import ArithmeticExpression
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame


class ArithmeticExpressionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_addition(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(5)

        arithmetic_expr = ArithmeticExpression(
            ExpressionType.ARITHMETIC_ADD,
            tpl_exp,
            const_exp
        )

        tuple1 = [5, 2, 3]

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)

        expected_value = [[6], [7], [8]]
        output_value  = arithmetic_expr.evaluate(input_batch)
        self.assertEqual(expected_value[0][0], output_value[0][0])

    def test_subtraction(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(5)

        arithmetic_expr = ArithmeticExpression(
            ExpressionType.ARITHMETIC_SUBTRACT,
            tpl_exp,
            const_exp
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)

        expected_value = [[-4], [-3], [-2]] 
        output_value  = arithmetic_expr.evaluate(input_batch)
        self.assertEqual(expected_value[0][0], output_value[0][0])

    def test_multiply(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(5)

        arithmetic_expr = ArithmeticExpression(
            ExpressionType.ARITHMETIC_MULTIPLY,
            tpl_exp,
            const_exp
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)

        expected_value = [[5.], [10.], [15.]]
        output_value  = arithmetic_expr.evaluate(input_batch)
        self.assertEqual(expected_value[0][0], output_value[0][0])

    def test_divide(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(5)

        arithmetic_expr = ArithmeticExpression(
            ExpressionType.ARITHMETIC_DIVIDE,
            tpl_exp,
            const_exp
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)

        expected_value = [[0.2], [0.4], [0.6]]
        output_value  = arithmetic_expr.evaluate(input_batch)
        self.assertEqual(expected_value[0][0], output_value[0][0])

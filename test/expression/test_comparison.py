import unittest
import numpy as np

from src.expression.abstract_expression import ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame


class ComparisonExpressionsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_comparison_compare_equal(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL,
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

        expected_value = [[True], [False], [False]]
        output_value  = cmpr_exp.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

    def test_comparison_compare_greater(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
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

        expected_value = [[False], [True], [True]]
        output_value  = cmpr_exp.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

    def test_comparison_compare_lesser(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(2)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_LESSER,
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

        expected_value = [[True], [False], [False]]
        output_value  = cmpr_exp.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

    def test_comparison_compare_geq(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_GEQ,
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

        expected_value = [[True], [True], [True]]
        output_value  = cmpr_exp.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

    def test_comparison_compare_leq(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(2)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_LEQ,
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

        expected_value = [[True], [True], [False]]
        output_value  = cmpr_exp.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

    def test_comparison_compare_neq(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_NEQ,
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

        expected_value = [[False], [True], [True]]
        output_value  = cmpr_exp.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

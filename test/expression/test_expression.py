import unittest

from src.expression.abstract_expression import ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.logical_expression import ExpressionLogical
from src.expression.tuple_value_expression import TupleValueExpression


class ExpressionsTest(unittest.TestCase):
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
        # ToDo implement a generic tuple class
        # to fetch the tuple from table
        tuple1 = [1, 2, 3]
        self.assertEqual(True, cmpr_exp.evaluate(tuple1, None))

    def test_constant_logical_expression(self):
        tpl_exp = TupleValueExpression(0)
        const_exp_1 = ConstantValueExpression(1)
        const_exp_0 = ConstantValueExpression(0)

        logical_expression = ExpressionLogical(const_exp_1, "AND", const_exp_1)
        self.assertEqual(True, logical_expression.evaluate())

        logical_expression = ExpressionLogical(const_exp_1, "OR", const_exp_1)
        self.assertEqual(True, logical_expression.evaluate())

        logical_expression = ExpressionLogical(const_exp_0, "OR", const_exp_1)
        self.assertEqual(True, logical_expression.evaluate())

        logical_expression = ExpressionLogical(const_exp_0, "AND", const_exp_1)
        self.assertEqual(False, logical_expression.evaluate())

        logical_expression = ExpressionLogical(const_exp_0, "AND", const_exp_0)
        self.assertEqual(False, logical_expression.evaluate())

        logical_expression = ExpressionLogical(const_exp_0, "OR", const_exp_0)
        self.assertEqual(False, logical_expression.evaluate())

        logical_expression = ExpressionLogical(const_exp_0, "NOR", const_exp_0)
        self.assertRaises(ValueError, logical_expression.evaluate())

        logical_expression = ExpressionLogical(const_exp_0, "XOR", const_exp_0)
        self.assertRaises(ValueError, logical_expression.evaluate())

        logical_expression = ExpressionLogical(const_exp_0, "^", const_exp_0)
        self.assertRaises(ValueError, logical_expression.evaluate())

        logical_expression = ExpressionLogical(const_exp_0, "&&", const_exp_0)
        self.assertRaises(ValueError, logical_expression.evaluate())

        logical_expression = ExpressionLogical(const_exp_0, "||", const_exp_0)
        self.assertRaises(ValueError, logical_expression.evaluate())

    def test_logical_expression(self):
        tpl_exp = TupleValueExpression(0)
        const_exp_1 = ConstantValueExpression(1)
        const_exp_0 = ConstantValueExpression(0)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL,
            tpl_exp,
            const_exp_1
        )

        self.assertEqual(0, tpl_exp.evaluate([1]))


if __name__ == '__main__':
    unittest.main()

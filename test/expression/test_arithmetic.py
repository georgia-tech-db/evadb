import unittest

from src.expression.abstract_expression import ExpressionType
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.expression.arithmetic_expression import ArithmeticExpression


class ArithmeticExpressionsTest(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_addition(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(5)

        cmpr_exp = ArithmeticExpression(
            ExpressionType.ARITHMETIC_ADD,
            tpl_exp,
            const_exp
        )

        tuple1 = [5, 2, 3]
        # 5+5 = 10
        self.assertEqual(10, cmpr_exp.evaluate(tuple1, None))

    def test_subtraction(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(5)

        cmpr_exp = ArithmeticExpression(
            ExpressionType.ARITHMETIC_SUBTRACT,
            tpl_exp,
            const_exp
        )

        tuple1 = [5, 2, 3]
        # 5-5 = 0
        self.assertEqual(0, cmpr_exp.evaluate(tuple1, None))
    
    def test_multiply(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(5)

        cmpr_exp = ArithmeticExpression(
            ExpressionType.ARITHMETIC_MULTIPLY,
            tpl_exp,
            const_exp
        )

        tuple1 = [5, 2, 3]
        # 5*5 = 25
        self.assertEqual(25, cmpr_exp.evaluate(tuple1, None))

    def test_divide(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(5)

        cmpr_exp = ArithmeticExpression(
            ExpressionType.ARITHMETIC_DIVIDE,
            tpl_exp,
            const_exp
        )

        tuple1 = [5, 2, 3]
        # 5/5 = 1
        self.assertEqual(1, cmpr_exp.evaluate(tuple1, None))
    


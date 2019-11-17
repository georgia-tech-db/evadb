import unittest


from src.expression.abstract_expression import ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.expression.logical_expression import ExpressionLogical


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

    def test_logical_expression(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_EQUAL,
            tpl_exp,
            const_exp
        )
        self.assertEqual(True, ExpressionLogical(cmpr_exp, "AND", cmpr_exp).evaluate())



if __name__ == '__main__':
    unittest.main()

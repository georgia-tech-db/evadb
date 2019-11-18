import unittest


from src.expression.abstract_expression import ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
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

    def test_comparison_compare_greater(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
            tpl_exp,
            const_exp
        )
        tuple1 = [2, 1, 1]
        self.assertEqual(True, cmpr_exp.evaluate(tuple1, None))

    def test_comparison_compare_lesser(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(2)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_LESSER,
            tpl_exp,
            const_exp
        )
        tuple1 = [1, 2, 3]
        self.assertEqual(True, cmpr_exp.evaluate(tuple1, None))
    
    def test_comparison_compare_geq(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_GEQ,
            tpl_exp,
            const_exp
        )
       
        # checking greater x>=1
        tuple1 = [2, 2, 3]
        self.assertEqual(True, cmpr_exp.evaluate(tuple1, None))
        # checking equal
        tuple2 = [1, 2, 3]
        self.assertEqual(True, cmpr_exp.evaluate(tuple2, None))

    def test_comparison_compare_leq(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(2)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_LEQ,
            tpl_exp,
            const_exp
        )
       
        # checking lesser x<=1
        tuple1 = [1, 2, 3]
        self.assertEqual(True, cmpr_exp.evaluate(tuple1, None))
        # checking equal
        tuple2 = [2, 2, 3]
        self.assertEqual(True, cmpr_exp.evaluate(tuple2, None))

    def test_comparison_compare_neq(self):
        tpl_exp = TupleValueExpression(0)
        const_exp = ConstantValueExpression(1)

        cmpr_exp = ComparisonExpression(
            ExpressionType.COMPARE_NEQ,
            tpl_exp,
            const_exp
        )
       
        # checking not equal x!=1
        tuple1 = [2, 2, 3]
        self.assertEqual(True, cmpr_exp.evaluate(tuple1, None))

        tuple1 = [3, 2, 3]
        self.assertEqual(True, cmpr_exp.evaluate(tuple1, None))
    
if __name__ == '__main__':
    unittest.main()

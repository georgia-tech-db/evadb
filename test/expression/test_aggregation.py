import unittest

from src.expression.abstract_expression import ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.aggregation_expression import AggregationExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression


class AggregationExpressionsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_aggregation_sum(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_SUM,
            None,
            columnName
        )
        tuple1 = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        self.assertEqual(6, aggr_expr.evaluate(tuple1, None))

    def test_aggregation_count(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_COUNT,
            None,
            columnName
        )
        tuple1 = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        self.assertEqual(3, aggr_expr.evaluate(tuple1, None))

    def test_aggregation_avg(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_AVG,
            None,
            columnName
        )
        tuple1 = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        self.assertEqual(2, aggr_expr.evaluate(tuple1, None))

    def test_aggregation_min(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_MIN,
            None,
            columnName
        )
        tuple1 = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        self.assertEqual(1, aggr_expr.evaluate(tuple1, None))

    def test_aggregation_max(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_MAX,
            None,
            columnName
        )
        tuple1 = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        self.assertEqual(3, aggr_expr.evaluate(tuple1, None))
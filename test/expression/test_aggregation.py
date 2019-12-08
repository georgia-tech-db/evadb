import unittest
import numpy as np

from src.expression.abstract_expression import ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.aggregation_expression import AggregationExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame
from src.models.inference.classifier_prediction import Prediction


class LogicalExpressionsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def test_aggregation_sum(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_SUM,
            None,
            columnName
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        outcome_1 = Prediction(frame_1, ["car", "bus"], [0.5, 0.6])
        outcome_2 = Prediction(frame_2, ["bus"], [0.5, 0.6])
        outcome_3 = Prediction(frame_3, ["car", "train"], [0.5, 0.6])
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)


        expected_value = 6
        output_value  = aggr_expr.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)
    
    def test_aggregation_count(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_COUNT,
            None,
            columnName
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        outcome_1 = Prediction(frame_1, ["car", "bus"], [0.5, 0.6])
        outcome_2 = Prediction(frame_2, ["bus"], [0.5, 0.6])
        outcome_3 = Prediction(frame_3, ["car", "train"], [0.5, 0.6])
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)


        expected_value = 3
        output_value  = aggr_expr.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

    
    def test_aggregation_avg(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_AVG,
            None,
            columnName
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        outcome_1 = Prediction(frame_1, ["car", "bus"], [0.5, 0.6])
        outcome_2 = Prediction(frame_2, ["bus"], [0.5, 0.6])
        outcome_3 = Prediction(frame_3, ["car", "train"], [0.5, 0.6])
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)

        expected_value = 2
        output_value  = aggr_expr.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)
    

    def test_aggregation_min(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_MIN,
            None,
            columnName
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        outcome_1 = Prediction(frame_1, ["car", "bus"], [0.5, 0.6])
        outcome_2 = Prediction(frame_2, ["bus"], [0.5, 0.6])
        outcome_3 = Prediction(frame_3, ["car", "train"], [0.5, 0.6])
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)

        expected_value = 1
        output_value  = aggr_expr.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)

    def test_aggregation_max(self):
        columnName = TupleValueExpression(0)
        aggr_expr = AggregationExpression(
            ExpressionType.AGGREGATION_MAX,
            None,
            columnName
        )

        frame_1 = Frame(1, np.ones((1, 1)), None)
        frame_2 = Frame(2, 2 * np.ones((1, 1)), None)
        frame_3 = Frame(3, 3 * np.ones((1, 1)), None)
        outcome_1 = Prediction(frame_1, ["car", "bus"], [0.5, 0.6])
        outcome_2 = Prediction(frame_2, ["bus"], [0.5, 0.6])
        outcome_3 = Prediction(frame_3, ["car", "train"], [0.5, 0.6])
        input_batch = FrameBatch(frames=[
            frame_1,
            frame_2,
            frame_3,
        ], info=None)

        expected_value = 3
        output_value  = aggr_expr.evaluate(input_batch)
        self.assertEqual(expected_value, output_value)
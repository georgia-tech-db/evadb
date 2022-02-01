import unittest
import pandas as pd
import numpy as np

from eva.executor.orderby_executor import OrderByExecutor
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.models.storage.batch import Batch
from eva.parser.types import ParserOrderBySortType
from test.executor.utils import DummyExecutor
from eva.planner.orderby_plan import OrderByPlan


class OrderByExecutorTest(unittest.TestCase):

    def test_should_return_sorted_frames(self):
        """
        data (3 batches):
        'A' 'B' 'C'
        [1, 1, 1]
        ----------
        [1, 5, 6]
        [4, 7, 10]
        ----------
        [2, 9, 7]
        [4, 1, 2]
        [4, 2, 4]
        """

        df1 = pd.DataFrame(
            np.array([[1, 1, 1]]), columns=['A', 'B', 'C'])
        df2 = pd.DataFrame(
            np.array([[1, 5, 6], [4, 7, 10]]), columns=['A', 'B', 'C'])
        df3 = pd.DataFrame(
            np.array([[2, 9, 7], [4, 1, 2],
                      [4, 2, 4]]), columns=['A', 'B', 'C'])

        batches = [Batch(frames=df) for df in [df1, df2, df3]]

        "query: .... ORDER BY A ASC, B DESC "

        plan = OrderByPlan(
            [(TupleValueExpression('A'), ParserOrderBySortType.ASC),
             (TupleValueExpression('B'), ParserOrderBySortType.DESC)])

        orderby_executor = OrderByExecutor(plan)
        orderby_executor.append_child(DummyExecutor(batches))

        sorted_batches = list(orderby_executor.exec())

        """
           A  B   C
        0  1  5   6
        1  1  1   1
        2  2  9   7
        3  4  7  10
        4  4  2   4
        5  4  1   2
        """
        expected_df1 = pd.DataFrame(
            np.array([[1, 5, 6]]), columns=['A', 'B', 'C'])
        expected_df2 = pd.DataFrame(
            np.array([[1, 1, 1], [2, 9, 7]]), columns=['A', 'B', 'C'])
        expected_df3 = pd.DataFrame(
            np.array([[4, 7, 10], [4, 2, 4],
                      [4, 1, 2]]), columns=['A', 'B', 'C'])

        expected_batches = [Batch(frames=df) for df in [
            expected_df1, expected_df2, expected_df3]]

        self.assertEqual(expected_batches[0], sorted_batches[0])
        self.assertEqual(expected_batches[1], sorted_batches[1])
        self.assertEqual(expected_batches[2], sorted_batches[2])

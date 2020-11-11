import unittest
# import pandas as pd

from src.executor.orderby_executor import OrderByExecutor
from src.models.storage.batch import Batch
from test.util import create_dataframe
from test.executor.utils import DummyExecutor
from src.planner.orderby_plan import OrderByPlan


class OrderByExecutorTest(unittest.TestCase):

    def test_should_return_sorted_frames(self):
        dataframe = create_dataframe(5)
        print()
        # print("Data Frame:\n", dataframe)
        batch = Batch(frames=dataframe)
        # print(batch)

        plan = OrderByPlan(None)
        orderby_executor = OrderByExecutor(plan)
        orderby_executor.append_child(DummyExecutor([batch]))

        expected = batch
        sorted = list(orderby_executor.exec())[0]

        print(expected)
        print(sorted)
        self.assertEqual(expected, sorted)

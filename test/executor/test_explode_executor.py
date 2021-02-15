import unittest
import pandas as pd
import numpy as np

from src.executor.explode_executor import ExplodeExecutor
from src.planner.explode_plan import ExplodePlan
from src.expression.tuple_value_expression import TupleValueExpression
from test.executor.utils import DummyExecutor

from src.models.storage.batch import Batch

class ExplodeExecutorTest(unittest.TestCase):

    def test_should_return_exploded_list(self):
        data_list = [[["car", "truck"], [0.5, 0.6]], [["plane", "car"], [0.3, 0.4]], [["car"], [0.5]]]
        df = pd.DataFrame(
            data_list, columns=['label', 'pred_score'])
        dfs = [df]

        batches = [Batch(frames=df) for df in dfs]

        columns = [TupleValueExpression("label"), TupleValueExpression("pred_score")]
        explode_plan = ExplodePlan(column_list=columns)
        explode_executor = ExplodeExecutor(explode_plan)
        explode_executor.append_child(DummyExecutor(batches))
        explode_executor.exec()

        reduced_batches = list(explode_executor.exec())

        expected_list = [["car", '0.5'], ["truck", '0.6'], ["plane", '0.3'], ["car", '0.4'], ["car", '0.5']]
        self.assertEqual(expected_list, reduced_batches[0].frames.values.tolist())

    def test_should_throw_no_such_column_error(self):
        pass


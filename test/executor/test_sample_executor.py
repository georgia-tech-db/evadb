import unittest
import pandas as pd
import numpy as np

from src.executor.sample_executor import SampleExecutor
from src.models.storage.batch import Batch
from test.executor.utils import DummyExecutor
from src.planner.sample_plan import SamplePlan
from src.expression.constant_value_expression import ConstantValueExpression


class SampleExecutorTest(unittest.TestCase):

    def test_should_return_smaller_num_rows(self):
        dfs = [pd.DataFrame(np.random.randint(0, 100, size=(100, 4)),
                            columns=list('ABCD')) for _ in range(4)]

        batches = [Batch(frames=df) for df in dfs]

        sample_value = 3

        plan = SamplePlan(ConstantValueExpression(sample_value))

        sample_executor = SampleExecutor(plan)
        sample_executor.append_child(DummyExecutor(batches))
        reduced_batches = list(sample_executor.exec())

        original = Batch.concat(batches)
        filter = range(0, len(original), sample_value)
        original = original._get_frames_from_indices(filter)
        original = Batch.concat([original])

        reduced = Batch.concat(reduced_batches)

        self.assertEqual(len(original), len(reduced))
        self.assertEqual(original, reduced)

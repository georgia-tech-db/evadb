# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
from test.executor.utils import DummyExecutor

import numpy as np
import pandas as pd

from eva.executor.sample_executor import SampleExecutor
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.models.storage.batch import Batch
from eva.planner.sample_plan import SamplePlan


class SampleExecutorTest(unittest.TestCase):
    def test_should_return_smaller_num_rows(self):
        dfs = [
            pd.DataFrame(np.random.randint(0, 100, size=(100, 4)), columns=list("ABCD"))
            for _ in range(4)
        ]

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

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

import pandas as pd

from eva.executor.function_scan_executor import FunctionScanExecutor
from eva.expression.function_expression import FunctionExpression
from eva.models.storage.batch import Batch
from eva.parser.alias import Alias


class FunctionScanExecutorTest(unittest.TestCase):
    def test_simple_function_scan(self):
        values = Batch(pd.DataFrame([1, 2, 3], columns=["a"]))
        expression = FunctionExpression(
            lambda: lambda x: x + 1,
            name="test",
            alias=Alias(
                "test",
                ["a"],
            ),
        )
        expression.projection_columns = "a"
        plan = type(
            "FunctionScanPlan",
            (),
            {"func_expr": expression, "do_unnest": False},
        )
        function_scan_executor = FunctionScanExecutor(plan)
        actual = list(function_scan_executor.exec(lateral_input=values))[0]
        expected = Batch(pd.DataFrame([2, 3, 4], columns=["test.a"]))
        self.assertEqual(expected, actual)

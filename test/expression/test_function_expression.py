# coding=utf-8
# Copyright 2018-2020 EVA
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

from src.expression.function_expression import FunctionExpression, \
    ExecutionMode
from src.models.storage.batch import Batch


class FunctionExpressionTest(unittest.TestCase):
    def test_should_work_for_function_without_children_eval_mode(self):
        expression = FunctionExpression(lambda x: x)
        values = [1, 2, 3]
        actual = expression.evaluate(values)
        self.assertEqual(values, actual)

    def test_should_update_the_batch_with_outcomes_in_exec_mode(self):
        values = [1, 2, 3]
        expression = FunctionExpression(lambda x: values,
                                        mode=ExecutionMode.EXEC, name="test")
        expected_batch = Batch(
            frames=pd.DataFrame(), outcomes={
                "test": [
                    1, 2, 3]})
        input_batch = Batch(frames=pd.DataFrame())
        expression.evaluate(input_batch)
        self.assertEqual(expected_batch, input_batch)

    def test_should_throw_assert_error_when_name_not_provided_exec_mode(self):
        self.assertRaises(AssertionError,
                          lambda _=None:
                          FunctionExpression(lambda x: [],
                                             mode=ExecutionMode.EXEC),
                          )

    def test_when_function_executor_with_a_child_should_allow_chaining(self):
        expression = FunctionExpression(lambda x: x)
        child = FunctionExpression(lambda x: list(map(lambda t: t + 1, x)))
        expression.append_child(child)
        values = [1, 2, 3]
        actual = expression.evaluate(values)
        expected = [2, 3, 4]
        self.assertEqual(expected, actual)

    def test_should_update_temp_outcomes_when_is_temp_set_exec_mode(self):
        values = [1, 2, 3]
        expression = FunctionExpression(lambda x: values,
                                        mode=ExecutionMode.EXEC,
                                        name="test", is_temp=True)
        expected_batch = Batch(
            frames=pd.DataFrame(),
            temp_outcomes={
                "test": [
                    1,
                    2,
                    3]})
        input_batch = Batch(frames=pd.DataFrame())
        expression.evaluate(input_batch)
        self.assertEqual(expected_batch, input_batch)

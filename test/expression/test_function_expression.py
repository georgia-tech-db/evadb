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
from mock import MagicMock, Mock, patch

from src.eva.constants import NO_GPU
from src.eva.expression.function_expression import FunctionExpression, \
    ExecutionMode
from src.eva.models.storage.batch import Batch
from src.eva.udfs.gpu_compatible import GPUCompatible


class FunctionExpressionTest(unittest.TestCase):
    def test_should_work_for_function_without_children_eval_mode(self):
        expression = FunctionExpression(lambda x: pd.DataFrame(x))
        values = Batch(pd.DataFrame([1, 2, 3]))
        actual = expression.evaluate(values)
        self.assertEqual(values, actual)

    def test_should_throw_assert_error_when_name_not_provided_exec_mode(self):
        self.assertRaises(AssertionError,
                          lambda _=None:
                          FunctionExpression(lambda x: [],
                                             mode=ExecutionMode.EXEC),
                          )

    def test_when_function_executor_with_a_child_should_allow_chaining(self):
        expression = FunctionExpression(lambda x:
                                        pd.DataFrame(x))
        child = FunctionExpression(lambda x: x + 1)
        expression.append_child(child)
        values = Batch(pd.DataFrame([1, 2, 3]))
        actual = expression.evaluate(values)
        expected = Batch(pd.DataFrame([2, 3, 4]))
        self.assertEqual(expected, actual)

    def test_should_filter_function_output(self):
        expression = FunctionExpression(lambda x: x + 1, output='id')
        values = pd.DataFrame({'id': [1, 2], 'data': [1, 2]})
        actual = expression.evaluate(Batch(values))
        expected = Batch(pd.DataFrame(values['id']) + 1)
        self.assertEqual(expected, actual)

    @patch('eva.expression.function_expression.Context')
    def test_function_move_the_device_to_gpu_if_compatible(self, context):
        context_instance = context.return_value
        mock_function = MagicMock(spec=GPUCompatible)
        gpu_mock_function = Mock(return_value=pd.DataFrame())
        gpu_device_id = '2'

        mock_function.to_device.return_value = gpu_mock_function
        context_instance.gpu_device.return_value = gpu_device_id

        expression = FunctionExpression(mock_function,
                                        mode=ExecutionMode.EXEC,
                                        name="test", is_temp=True)

        input_batch = Batch(frames=pd.DataFrame())
        expression.evaluate(input_batch)
        mock_function.to_device.assert_called_with(gpu_device_id)
        gpu_mock_function.assert_called()

    def test_should_use_the_same_function_if_not_gpu_compatible(self):
        mock_function = MagicMock(return_value=pd.DataFrame())

        expression = FunctionExpression(mock_function,
                                        mode=ExecutionMode.EXEC,
                                        name="test", is_temp=True)

        input_batch = Batch(frames=pd.DataFrame())
        expression.evaluate(input_batch)
        mock_function.assert_called()

    @patch('eva.expression.function_expression.Context')
    def test_should_execute_same_function_if_no_gpu(self, context):
        context_instance = context.return_value
        mock_function = MagicMock(spec=GPUCompatible,
                                  return_value=pd.DataFrame())

        context_instance.gpu_device.return_value = NO_GPU

        expression = FunctionExpression(mock_function,
                                        mode=ExecutionMode.EXEC,
                                        name="test", is_temp=True)

        input_batch = Batch(frames=pd.DataFrame())
        expression.evaluate(input_batch)
        mock_function.assert_called()

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
from mock import MagicMock, Mock, patch

from eva.constants import NO_GPU
from eva.expression.function_expression import FunctionExpression
from eva.models.storage.batch import Batch
from eva.parser.alias import Alias
from eva.udfs.gpu_compatible import GPUCompatible


class FunctionExpressionTest(unittest.TestCase):
    @patch("eva.expression.function_expression.Context")
    def test_function_move_the_device_to_gpu_if_compatible(self, context):
        context_instance = context.return_value
        mock_function = MagicMock(spec=GPUCompatible)
        gpu_mock_function = Mock(return_value=pd.DataFrame())
        gpu_device_id = "2"

        mock_function.to_device.return_value = gpu_mock_function
        context_instance.gpu_device.return_value = gpu_device_id

        expression = FunctionExpression(
            lambda: mock_function, name="test", alias=Alias("func_expr")
        )
        input_batch = Batch(frames=pd.DataFrame())
        expression.evaluate(input_batch)
        mock_function.to_device.assert_called_with(gpu_device_id)
        gpu_mock_function.assert_called()

    def test_should_use_the_same_function_if_not_gpu_compatible(self):
        mock_function = MagicMock(return_value=pd.DataFrame())

        expression = FunctionExpression(
            lambda: mock_function, name="test", alias=Alias("func_expr")
        )
        input_batch = Batch(frames=pd.DataFrame())
        expression.evaluate(input_batch)
        mock_function.assert_called()

    @patch("eva.expression.function_expression.Context")
    def test_should_execute_same_function_if_no_gpu(self, context):
        context_instance = context.return_value
        mock_function = MagicMock(spec=GPUCompatible, return_value=pd.DataFrame())

        context_instance.gpu_device.return_value = NO_GPU

        expression = FunctionExpression(
            lambda: mock_function, name="test", alias=Alias("func_expr")
        )

        input_batch = Batch(frames=pd.DataFrame())
        expression.evaluate(input_batch)
        mock_function.assert_called()

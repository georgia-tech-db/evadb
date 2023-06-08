# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from mock import patch

from evadb.constants import NO_GPU
from evadb.executor.execution_context import Context


class ExecutionContextTest(unittest.TestCase):
    @patch("evadb.executor.execution_context.ConfigurationManager")
    @patch("evadb.executor.execution_context.get_gpu_count")
    @patch("evadb.executor.execution_context.is_gpu_available")
    def test_CUDA_VISIBLE_DEVICES_gets_populated_from_config(
        self, gpu_check, get_gpu_count, cfm
    ):
        gpu_check.return_value = True
        get_gpu_count.return_value = 3
        cfm.return_value.get_value.return_value = [0, 1]
        context = Context()

        self.assertEqual(context.gpus, [0, 1])

    @patch("evadb.executor.execution_context.ConfigurationManager")
    @patch("evadb.executor.execution_context.os")
    @patch("evadb.executor.execution_context.get_gpu_count")
    @patch("evadb.executor.execution_context.is_gpu_available")
    def test_CUDA_VISIBLE_DEVICES_gets_populated_from_environment_if_no_config(
        self, is_gpu, get_gpu_count, os, cfm
    ):
        is_gpu.return_value = True
        cfm.return_value.get_value.return_value = []
        get_gpu_count.return_value = 3
        os.environ.get.return_value = "0,1"
        context = Context()
        os.environ.get.assert_called_with("CUDA_VISIBLE_DEVICES", "")

        self.assertEqual(context.gpus, [0, 1])

    @patch("evadb.executor.execution_context.ConfigurationManager")
    @patch("evadb.executor.execution_context.os")
    @patch("evadb.executor.execution_context.get_gpu_count")
    @patch("evadb.executor.execution_context.is_gpu_available")
    def test_CUDA_VISIBLE_DEVICES_should_be_empty_if_nothing_provided(
        self, gpu_check, get_gpu_count, os, cfm
    ):
        gpu_check.return_value = True
        get_gpu_count.return_value = 3
        cfm.return_value.get_value.return_value = []
        os.environ.get.return_value = ""
        context = Context()
        os.environ.get.assert_called_with("CUDA_VISIBLE_DEVICES", "")

        self.assertEqual(context.gpus, [])

    @patch("evadb.executor.execution_context.ConfigurationManager")
    @patch("evadb.executor.execution_context.os")
    @patch("evadb.executor.execution_context.is_gpu_available")
    def test_gpus_ignores_config_if_no_gpu_available(self, gpu_check, os, cfm):
        gpu_check.return_value = False
        cfm.return_value.get_value.return_value = [0, 1, 2]
        os.environ.get.return_value = "0,1,2"
        context = Context()

        self.assertEqual(context.gpus, [])

    @patch("evadb.executor.execution_context.ConfigurationManager")
    @patch("evadb.executor.execution_context.os")
    @patch("evadb.executor.execution_context.is_gpu_available")
    def test_gpu_device_should_return_NO_GPU_if_GPU_not_available(
        self, gpu_check, os, cfm
    ):
        gpu_check.return_value = True
        cfm.return_value.get_value.return_value = []
        os.environ.get.return_value = ""
        context = Context()
        os.environ.get.assert_called_with("CUDA_VISIBLE_DEVICES", "")

        self.assertEqual(context.gpu_device(), NO_GPU)

    @patch("evadb.executor.execution_context.ConfigurationManager")
    @patch("evadb.executor.execution_context.get_gpu_count")
    @patch("evadb.executor.execution_context.is_gpu_available")
    def test_should_return_random_gpu_ID_if_available(
        self, gpu_check, get_gpu_count, cfm
    ):
        gpu_check.return_value = True
        get_gpu_count.return_value = 1
        cfm.return_value.get_value.return_value = [0, 1, 2]
        context = Context()

        selected_device = context.gpu_device()
        self.assertEqual(selected_device, 0)

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

from mock import patch

from eva.constants import NO_GPU
from eva.executor.execution_context import Context


class ExecutionContextTest(unittest.TestCase):
    @patch("eva.executor.execution_context.ConfigurationManager")
    @patch("eva.executor.execution_context.socket")
    @patch("eva.executor.execution_context.is_gpu_available")
    def test_gpu_devices_gets_populated_from_config(self, gpu_check, socket, cfm):
        gpu_check.return_value = True
        socket.gethostname.return_value = "host"
        socket.gethostbyaddr.return_value = (
            "local",
            ["another-hostname", "other-possible"],
            ["address2"],
        )
        cfm.return_value.get_value.return_value = {"address2": ["0", "1", "2"]}
        context = Context()

        self.assertEqual(context.gpus, ["0", "1", "2"])

    @patch("eva.executor.execution_context.ConfigurationManager")
    @patch("eva.executor.execution_context.os")
    @patch("eva.executor.execution_context.socket")
    @patch("eva.executor.execution_context.is_gpu_available")
    def test_gpu_devices_gets_populated_from_environment_if_no_config(
        self, is_gpu, socket, os, cfm
    ):
        is_gpu.return_value = True

        socket.gethostname.return_value = "host"
        socket.gethostbyaddr.return_value = (
            "local",
            ["another-hostname", "other-possible"],
            ["address2"],
        )
        cfm.return_value.get_value.return_value = {"address3": ["0", "1", "2"]}
        os.environ.get.return_value = "0,1,2"
        context = Context()
        os.environ.get.assert_called_with("GPU_DEVICES", "")

        self.assertEqual(context.gpus, ["0", "1", "2"])

    @patch("eva.executor.execution_context.ConfigurationManager")
    @patch("eva.executor.execution_context.os")
    @patch("eva.executor.execution_context.socket")
    @patch("eva.executor.execution_context.is_gpu_available")
    def test_gpu_devices_should_be_empty_if_nothing_provided(
        self, gpu_check, socket, os, cfm
    ):
        gpu_check.return_value = True
        socket.gethostname.return_value = "host"
        socket.gethostbyaddr.return_value = (
            "local",
            ["another-hostname", "other-possible"],
            ["address2"],
        )
        cfm.return_value.get_value.return_value = {"address3": ["0", "1", "2"]}
        os.environ.get.return_value = ""
        context = Context()
        os.environ.get.assert_called_with("GPU_DEVICES", "")

        self.assertEqual(context.gpus, [])

    @patch("eva.executor.execution_context.ConfigurationManager")
    @patch("eva.executor.execution_context.os")
    @patch("eva.executor.execution_context.socket")
    @patch("eva.executor.execution_context.is_gpu_available")
    def test_gpus_ignores_config_if_no_gpu_available(self, gpu_check, socket, os, cfm):
        gpu_check.return_value = False
        socket.gethostname.return_value = "host"
        socket.gethostbyaddr.return_value = (
            "local",
            ["another-hostname", "other-possible"],
            ["address2"],
        )
        cfm.return_value.get_value.return_value = {"address3": ["0", "1", "2"]}
        os.environ.get.return_value = "0,1,2"
        context = Context()

        self.assertEqual(context.gpus, [])

    @patch("eva.executor.execution_context.ConfigurationManager")
    @patch("eva.executor.execution_context.os")
    @patch("eva.executor.execution_context.socket")
    @patch("eva.executor.execution_context.is_gpu_available")
    def test_gpu_device_should_return_NO_GPU_if_GPU_not_available(
        self, gpu_check, socket, os, cfm
    ):
        gpu_check.return_value = True
        socket.gethostname.return_value = "host"
        socket.gethostbyaddr.return_value = (
            "local",
            ["another-hostname", "other-possible"],
            ["address2"],
        )
        cfm.return_value.get_value.return_value = None
        os.environ.get.return_value = ""
        context = Context()
        os.environ.get.assert_called_with("GPU_DEVICES", "")

        self.assertEqual(context.gpu_device(), NO_GPU)

    @patch("eva.executor.execution_context.ConfigurationManager")
    @patch("eva.executor.execution_context.socket")
    @patch("eva.executor.execution_context.is_gpu_available")
    @patch("eva.executor.execution_context.random")
    def test_should_return_random_gpu_ID_if_available(
        self, random, gpu_check, socket, cfm
    ):
        random.choice.return_value = "2"
        gpu_check.return_value = True
        socket.gethostname.return_value = "host"
        socket.gethostbyaddr.return_value = (
            "local",
            ["another-hostname", "other-possible"],
            ["address2"],
        )
        cfm.return_value.get_value.return_value = {"address2": ["0", "1", "2"]}
        context = Context()

        selected_device = context.gpu_device()

        random.choice.assert_called_with(context.gpus)
        self.assertEqual(selected_device, "2")

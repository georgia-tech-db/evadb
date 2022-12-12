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
from pathlib import Path

from mock import MagicMock, patch

from eva.readers.opencv_reader import OpenCVReader
from eva.utils.generic_utils import (
    generate_file_path,
    is_gpu_available,
    path_to_class,
    str_to_class,
)


class ModulePathTest(unittest.TestCase):
    def test_should_return_correct_class_for_string(self):
        vl = str_to_class("eva.readers.opencv_reader.OpenCVReader")
        self.assertEqual(vl, OpenCVReader)

    @unittest.skip(
        "This returns opecv_reader.OpenCVReader \
                   instead of eva.readers.opencv_reader.OpenCVReader"
    )
    def test_should_return_correct_class_for_path(self):
        vl = path_to_class("eva/readers/opencv_reader.py", "OpenCVReader")
        self.assertEqual(vl, OpenCVReader)

    def test_should_raise_if_class_does_not_exists(self):
        with self.assertRaises(RuntimeError):
            path_to_class("eva/readers/opencv_reader.py", "OpenCV")

    def test_should_use_torch_to_check_if_gpu_is_available(self):
        # Emulate a missing import
        # Ref: https://stackoverflow.com/a/2481588
        try:
            import builtins
        except ImportError:
            import __builtin__ as builtins
        realimport = builtins.__import__

        def missing_import(name, globals, locals, fromlist, level):
            if name == "torch":
                raise ImportError
            return realimport(name, globals, locals, fromlist, level)

        builtins.__import__ = missing_import
        self.assertFalse(is_gpu_available())

        # Switch back to builtin import
        builtins.__import__ = realimport
        is_gpu_available()

    @patch("eva.utils.generic_utils.ConfigurationManager")
    def test_should_return_a_random_full_path(self, mock_conf):
        mock_conf_inst = MagicMock()
        mock_conf.return_value = mock_conf_inst
        mock_conf_inst.get_value.return_value = "eva_datasets"
        expected = Path("eva_datasets").resolve()
        actual = generate_file_path("test")
        self.assertTrue(actual.is_absolute())
        # Root directory must be the same, filename is random
        self.assertTrue(expected.match(str(actual.parent)))

        mock_conf_inst.get_value.return_value = None
        self.assertRaises(KeyError, generate_file_path)

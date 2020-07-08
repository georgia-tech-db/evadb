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
from mock import patch, MagicMock
from pathlib import Path

from src.utils.generic_utils import str_to_class, generate_file_path
from src.readers.opencv_reader import OpenCVReader


class ModulePathTest(unittest.TestCase):

    def test_should_return_correct_class_for_string(self):
        vl = str_to_class("src.readers.opencv_reader.OpenCVReader")
        self.assertEqual(vl, OpenCVReader)

    @patch('src.utils.generic_utils.ConfigurationManager')
    def test_should_return_a_randon_full_path(self, mock_conf):
        mock_conf_inst = MagicMock()
        mock_conf.return_value = mock_conf_inst
        mock_conf_inst.get_value.return_value = 'eva_datasets'
        expected = Path('eva_datasets').resolve()
        actual = generate_file_path('test')
        self.assertTrue(actual.is_absolute())
        # Root directory must be the same, filename is random
        self.assertTrue(expected.match(str(actual.parent)))

        mock_conf_inst.get_value.return_value = None
        self.assertRaises(KeyError, generate_file_path)

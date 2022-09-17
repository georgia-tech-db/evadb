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
import pytest

from eva.configuration.configuration_manager import ConfigurationManager


class ConfigurationManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ConfigurationManager()
        return super().setUp()

    def test_configuration_manager_read_nonexistent_key(self):
        value = self.config.get_value("core", "datasets_dir")
        self.assertNotEqual(value, None)

    def test_configuration_manager_read_invalid_category(self):
        with pytest.raises(KeyError):
            value = self.config.get_value("invalid", "")
            self.assertEqual(value, None)

    def test_configuration_manager_read_invalid_key(self):
        with pytest.raises(KeyError):
            value = self.config.get_value("core", "invalid")
            self.assertEqual(value, None)

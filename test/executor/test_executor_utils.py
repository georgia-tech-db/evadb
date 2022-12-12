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

from eva.executor.executor_utils import ExecutorError, handle_if_not_exists


class ExecutorUtilsTest(unittest.TestCase):
    @patch("eva.executor.executor_utils.CatalogManager.check_table_exists")
    def test_handle_if_not_exists_raises_error(self, check_mock):
        check_mock.return_value = True
        with self.assertRaises(ExecutorError):
            handle_if_not_exists(check_mock, False)

    @patch("eva.executor.executor_utils.CatalogManager.check_table_exists")
    def test_handle_if_not_exists_return_True(self, check_mock):
        check_mock.return_value = True
        self.assertTrue(handle_if_not_exists(check_mock, True))

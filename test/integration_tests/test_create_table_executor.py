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

from eva.executor.executor_utils import ExecutorError
from eva.server.command_handler import execute_query_fetch_all


class CreateTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_currently_cannot_create_boolean_table(self):
        query = """ CREATE TABLE BooleanTable( A BOOLEAN);"""

        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(query)

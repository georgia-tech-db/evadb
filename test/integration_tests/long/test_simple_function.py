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
from test.util import suffix_pytest_xdist_worker_id_to_dir

import pytest
import pandas as pd

from evadb.configuration.constants import EvaDB_DATABASE_DIR, EvaDB_ROOT_DIR
from evadb.interfaces.relational.db import connect
from evadb.server.command_handler import execute_query_fetch_all

def Func_SimpleUDF(cls, x:int)->int:
    return x + 10

@pytest.mark.notparallel
class SimpleFunctionTests(unittest.TestCase):
    def setUp(self):
        self.db_dir = suffix_pytest_xdist_worker_id_to_dir(EvaDB_DATABASE_DIR)
        self.conn = connect(self.db_dir)
        self.evadb = self.conn._evadb
        self.evadb.catalog().reset()

    def tearDown(self):
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS test_table;")
        execute_query_fetch_all(self.evadb, "DROP FUNCTION IF EXISTS My_SimpleUDF;")
        execute_query_fetch_all(self.evadb, "DROP FUNCTION IF EXISTS Func_SimpleUDF;")

    def test_from_file(self):
        cursor = self.conn.cursor()

        execute_query_fetch_all(self.evadb, "CREATE TABLE IF NOT EXISTS test_table (val INTEGER);")
        cursor.insert("test_table", "(val)", "(1)").df()

        cursor.create_function(
            "My_SimpleUDF",
            True,
            f"{EvaDB_ROOT_DIR}/evadb/functions/My_SimpleUDF.py",
        ).df()

        result = cursor.query("SELECT My_SimpleUDF(val) FROM test_table;").df()
        expected = pd.DataFrame({'output': [6]})

        self.assertTrue(expected.equals(result)) 

    def test_from_function(self):
        cursor = self.conn.cursor()

        execute_query_fetch_all(self.evadb, "CREATE TABLE IF NOT EXISTS test_table (val INTEGER);")
        cursor.insert("test_table", "(val)", "(1)").df()

        cursor.create_simple_function(
            "Func_SimpleUDF",
            Func_SimpleUDF,
            True,
        ).df()

        result = cursor.query("SELECT Func_SimpleUDF(val) FROM test_table;").df()
        expected = pd.DataFrame({'output': [11]})

        self.assertTrue(expected.equals(result))       
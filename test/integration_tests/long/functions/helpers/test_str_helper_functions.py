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
from test.util import get_evadb_for_testing

from evadb.server.command_handler import execute_query_fetch_all


class StrHelperTest(unittest.TestCase):
    def setUp(self) -> None:
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        create_table_query = """CREATE TABLE IF NOT EXISTS Test (
             input TEXT);
                """
        execute_query_fetch_all(self.evadb, create_table_query)

        test_prompts = ["EvaDB"]

        for prompt in test_prompts:
            insert_query = f"""INSERT INTO Test (input) VALUES ('{prompt}')"""
            execute_query_fetch_all(self.evadb, insert_query)

    def tearDown(self) -> None:
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS Test;")

    def test_upper_function(self):
        function_name = "UPPER"
        execute_query_fetch_all(self.evadb, f"DROP FUNCTION IF EXISTS {function_name};")
        create_function_query = f"""CREATE FUNCTION IF NOT EXISTS {function_name}
        INPUT  (inp ANYTYPE)
        OUTPUT (output NDARRAY STR(ANYDIM))
        TYPE HelperFunction
        IMPL 'evadb/functions/helpers/upper.py';
        """
        execute_query_fetch_all(self.evadb, create_function_query)
        query = "SELECT UPPER(input) FROM Test;"
        output_batch = execute_query_fetch_all(self.evadb, query)
        self.assertEqual(len(output_batch), 1)
        self.assertEqual(output_batch.frames["upper.output"][0], "EVADB")

        query = "SELECT UPPER('test5')"
        output_batch = execute_query_fetch_all(self.evadb, query)
        self.assertEqual(len(output_batch), 1)
        self.assertEqual(output_batch.frames["upper.output"][0], "TEST5")

    def test_lower_function(self):
        function_name = "LOWER"
        execute_query_fetch_all(self.evadb, f"DROP FUNCTION IF EXISTS {function_name};")
        create_function_query = f"""CREATE FUNCTION IF NOT EXISTS {function_name}
        INPUT  (inp ANYTYPE)
        OUTPUT (output NDARRAY STR(ANYDIM))
        TYPE HelperFunction
        IMPL 'evadb/functions/helpers/lower.py';
        """
        execute_query_fetch_all(self.evadb, create_function_query)
        query = "SELECT LOWER(input) FROM Test;"
        output_batch = execute_query_fetch_all(self.evadb, query)
        self.assertEqual(len(output_batch), 1)
        self.assertEqual(output_batch.frames["lower.output"][0], "evadb")

        query = "SELECT LOWER('TEST5')"
        output_batch = execute_query_fetch_all(self.evadb, query)
        self.assertEqual(len(output_batch), 1)
        self.assertEqual(output_batch.frames["lower.output"][0], "test5")

    def test_concat_function(self):
        function_name = "CONCAT"
        execute_query_fetch_all(self.evadb, f"DROP FUNCTION IF EXISTS {function_name};")
        create_function_query = f"""CREATE FUNCTION IF NOT EXISTS {function_name}
        INPUT  (inp ANYTYPE)
        OUTPUT (output NDARRAY STR(ANYDIM))
        TYPE HelperFunction
        IMPL 'evadb/functions/helpers/concat.py';
        """
        execute_query_fetch_all(self.evadb, create_function_query)

        execute_query_fetch_all(self.evadb, "DROP FUNCTION IF EXISTS UPPER;")
        create_function_query = """CREATE FUNCTION IF NOT EXISTS UPPER
        INPUT  (inp ANYTYPE)
        OUTPUT (output NDARRAY STR(ANYDIM))
        TYPE HelperFunction
        IMPL 'evadb/functions/helpers/upper.py';
        """

        execute_query_fetch_all(self.evadb, create_function_query)
        query = "SELECT CONCAT(UPPER('Eva'), 'DB');"
        output_batch = execute_query_fetch_all(self.evadb, query)
        self.assertEqual(len(output_batch), 1)
        self.assertEqual(output_batch.frames["concat.output"][0], "EVADB")

        query = "SELECT CONCAT(input, '.com') FROM Test;"
        output_batch = execute_query_fetch_all(self.evadb, query)
        self.assertEqual(len(output_batch), 1)
        self.assertEqual(output_batch.frames["concat.output"][0], "EvaDB.com")

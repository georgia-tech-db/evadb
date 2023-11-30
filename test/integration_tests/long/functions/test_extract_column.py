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

import os
import unittest
from test.markers import chatgpt_skip_marker
from test.util import get_evadb_for_testing

import pandas as pd

from evadb.server.command_handler import execute_query_fetch_all


class ExtractColumnTest(unittest.TestCase):
    def setUp(self) -> None:
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        create_table_query = """CREATE TABLE IF NOT EXISTS InputUnstructured (
                input_rows TEXT)
            """

        execute_query_fetch_all(self.evadb, create_table_query)

        input_row = "My keyboard has stopped working"

        insert_query = f"""INSERT INTO InputUnstructured (input_rows) VALUES ("{input_row}")"""
        execute_query_fetch_all(self.evadb, insert_query)
        # Add actual API key here
        os.environ["OPENAI_API_KEY"] = "sk-..."

    def tearDown(self) -> None:
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS InputUnstructured;")

    @chatgpt_skip_marker
    def test_extract_column_function(self):
        function_name = "ExtractColumn"
        execute_query_fetch_all(self.evadb, f"DROP FUNCTION IF EXISTS {function_name};")

        create_function_query = f"""CREATE FUNCTION IF NOT EXISTS {function_name} IMPL 'evadb/functions/extract_column.py';"""

        execute_query_fetch_all(self.evadb, create_function_query)

        extract_columns_query = f"SELECT {function_name}('Issue Component','The component that is causing the issue', 'string less than 2 words', input_rows) FROM InputUnstructured;"
        output_batch = execute_query_fetch_all(self.evadb, extract_columns_query)
        self.assertEqual(output_batch.columns, ["chatgpt.response"])

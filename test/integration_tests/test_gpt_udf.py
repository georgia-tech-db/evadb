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
from unittest.mock import MagicMock

from mock import patch
import pandas as pd
from eva.models.storage.batch import Batch

from eva.server.command_handler import execute_query_fetch_all


class GPTUDFsTest(unittest.TestCase):
    @patch("eva.udfs.gpt_udf.openai.ChatCompletion.create")
    def test_gpt_udf(self, mock_req):
        udf_name = "ChatGPT"

        execute_query_fetch_all(f"DROP UDF IF EXISTS {udf_name};")

        self.csv_file_path = "test/data/queries.csv"

        create_udf_query = f"""CREATE UDF {udf_name}
            IMPL 'eva/udfs/gpt_udf.py'
        """
        execute_query_fetch_all(create_udf_query)

        execute_query_fetch_all("DROP TABLE MyTextCSV;")
        create_table_query = """CREATE TABLE IF NOT EXISTS MyTextCSV (
                id INTEGER UNIQUE,
                prompt TEXT (100),
                query TEXT (100)
            );"""
        execute_query_fetch_all(create_table_query)

        csv_query = f"""LOAD CSV '{self.csv_file_path}' INTO MyTextCSV;"""
        execute_query_fetch_all(csv_query)

        mock_response_obj = MagicMock()
        mock_response_obj.message.content = "mock message"
        mock_req.return_value.choices = [mock_response_obj]

        gpt_query = f"SELECT {udf_name}(prompt, query) FROM MyTextCSV;"
        output_batch = execute_query_fetch_all(gpt_query)
        expected_output = Batch(pd.DataFrame(["mock message"], columns=["response"]))
        self.assertEqual(len(output_batch), 1)
        self.assertEqual(len(list(output_batch.columns)), 1)
        self.assertEqual(output_batch, expected_output)

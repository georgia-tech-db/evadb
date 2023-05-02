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
from test.markers import ray_skip_marker
from unittest.mock import MagicMock

import pandas as pd
from mock import patch

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all


class ChatGPTTest(unittest.TestCase):
    def setUp(self) -> None:
        CatalogManager().reset()
        create_table_query = """CREATE TABLE IF NOT EXISTS MyTextCSV (
                id INTEGER UNIQUE,
                prompt TEXT (100),
                query TEXT (100)
            );"""
        execute_query_fetch_all(create_table_query)

        self.csv_file_path = "test/data/queries.csv"
        csv_query = f"""LOAD CSV '{self.csv_file_path}' INTO MyTextCSV;"""
        execute_query_fetch_all(csv_query)

    def tearDown(self) -> None:
        execute_query_fetch_all("DROP TABLE IF EXISTS MyTextCSV;")

    @ray_skip_marker
    @patch("eva.udfs.gpt_udf.openai.ChatCompletion.create")
    def test_gpt_udf(self, mock_req):
        # set dummy api key
        ConfigurationManager().update_value("third_party", "openai_api_key", "my_key")

        udf_name = "ChatGPT"
        execute_query_fetch_all(f"DROP UDF IF EXISTS {udf_name};")

        create_udf_query = f"""CREATE UDF {udf_name}
            IMPL 'eva/udfs/gpt_udf.py'
        """
        execute_query_fetch_all(create_udf_query)

        mock_response_obj = MagicMock()
        mock_response_obj.message.content = "mock message"
        mock_req.return_value.choices = [mock_response_obj]

        gpt_query = f"SELECT {udf_name}(prompt, query) FROM MyTextCSV;"
        output_batch = execute_query_fetch_all(gpt_query)
        expected_output = Batch(
            pd.DataFrame(["mock message"], columns=["chatgpt.response"])
        )

        self.assertEqual(len(output_batch), 1)
        self.assertEqual(len(list(output_batch.columns)), 1)
        self.assertEqual(output_batch, expected_output)

    def test_gpt_udf_no_key(self):
        ConfigurationManager().update_value("third_party", "openai_api_key", "")
        udf_name = "ChatGPT"
        execute_query_fetch_all(f"DROP UDF IF EXISTS {udf_name};")

        with self.assertRaises(ExecutorError):
            create_udf_query = f"""CREATE UDF {udf_name}
            IMPL 'eva/udfs/gpt_udf.py'
            """
            execute_query_fetch_all(create_udf_query)

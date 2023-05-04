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


def create_dummy_csv_file() -> str:
    config = ConfigurationManager()
    tmp_dir_from_config = config.get_value("storage", "tmp_dir")

    df_dict = {
        "prompt": ["summarize"],
        "content": [
            "There are times when the night sky glows with bands of color. The bands may begin as cloud shapes and then spread into a great arc across the entire sky. They may fall in folds like a curtain drawn across the heavens. The lights usually grow brighter, then suddenly dim. During this time the sky glows with pale yellow, pink, green, violet, blue, and red. These lights are called the Aurora Borealis. Some people call them the Northern Lights. Scientists have been watching them for hundreds of years. They are not quite sure what causes them"
        ],
    }
    df = pd.DataFrame(df_dict, columns=["id", "prompt", "content"])

    dummy_file_path = tmp_dir_from_config + "/queries.csv"
    df.to_csv(dummy_file_path)

    return dummy_file_path


class OpenAIChatCompletionTest(unittest.TestCase):
    def setUp(self) -> None:
        CatalogManager().reset()
        create_table_query = """CREATE TABLE IF NOT EXISTS MyTextCSV (
                id INTEGER UNIQUE,
                prompt TEXT (100),
                content TEXT (100)
            );"""
        execute_query_fetch_all(create_table_query)

        self.csv_file_path = create_dummy_csv_file()

        csv_query = f"""LOAD CSV '{self.csv_file_path}' INTO MyTextCSV;"""
        execute_query_fetch_all(csv_query)

    def tearDown(self) -> None:
        execute_query_fetch_all("DROP TABLE IF EXISTS MyTextCSV;")

    @ray_skip_marker
    @patch("eva.udfs.openai_chat_completion_udf.openai.ChatCompletion.create")
    def test_openai_chat_completion_udf(self, mock_req):
        # set dummy api key
        ConfigurationManager().update_value("third_party", "openai_api_key", "my_key")

        udf_name = "OpenAIChatCompletion"
        execute_query_fetch_all(f"DROP UDF IF EXISTS {udf_name};")

        create_udf_query = f"""CREATE UDF {udf_name}
            IMPL 'eva/udfs/openai_chat_completion_udf.py'
            'model' 'gpt-3.5-turbo'
        """
        execute_query_fetch_all(create_udf_query)

        mock_response_obj = MagicMock()
        mock_response_obj.message.content = "mock message"
        mock_req.return_value.choices = [mock_response_obj]

        gpt_query = f"SELECT {udf_name}(prompt, content) FROM MyTextCSV;"
        output_batch = execute_query_fetch_all(gpt_query)
        expected_output = Batch(
            pd.DataFrame(["mock message"], columns=["openaichatcompletion.response"])
        )
        self.assertEqual(output_batch, expected_output)

        # test without providing model name
        execute_query_fetch_all(f"DROP UDF IF EXISTS {udf_name};")
        create_udf_query = f"""CREATE UDF {udf_name}
            IMPL 'eva/udfs/openai_chat_completion_udf.py'
        """
        execute_query_fetch_all(create_udf_query)

        gpt_query = f"SELECT {udf_name}(prompt, content) FROM MyTextCSV;"
        output_batch = execute_query_fetch_all(gpt_query)
        self.assertEqual(output_batch, expected_output)

    def test_gpt_udf_no_key(self):
        ConfigurationManager().update_value("third_party", "openai_api_key", "")
        udf_name = "ChatGPT"
        execute_query_fetch_all(f"DROP UDF IF EXISTS {udf_name};")

        with self.assertRaises(ExecutorError):
            create_udf_query = f"""CREATE UDF {udf_name}
            IMPL 'eva/udfs/openai_chat_completion_udf.py'
            """
            execute_query_fetch_all(create_udf_query)

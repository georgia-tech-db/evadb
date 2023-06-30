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
from test.markers import chatgpt_skip_marker
from test.util import get_evadb_for_testing

import pandas as pd

from evadb.server.command_handler import execute_query_fetch_all


def create_dummy_csv_file(config) -> str:
    tmp_dir_from_config = config.get_value("storage", "tmp_dir")

    df_dict = [
        {
            "prompt": "summarize",
            "content": "There are times when the night sky glows with bands of color. The bands may begin as cloud shapes and then spread into a great arc across the entire sky. They may fall in folds like a curtain drawn across the heavens. The lights usually grow brighter, then suddenly dim. During this time the sky glows with pale yellow, pink, green, violet, blue, and red. These lights are called the Aurora Borealis. Some people call them the Northern Lights. Scientists have been watching them for hundreds of years. They are not quite sure what causes them",
        }
    ]
    df = pd.DataFrame(df_dict)

    dummy_file_path = tmp_dir_from_config + "/queries.csv"
    df.to_csv(dummy_file_path)

    return dummy_file_path


class ChatGPTTest(unittest.TestCase):
    def setUp(self) -> None:
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        create_table_query = """CREATE TABLE IF NOT EXISTS MyTextCSV (
                prompt TEXT(30),
                content TEXT (100)
            );"""
        execute_query_fetch_all(self.evadb, create_table_query)

        self.csv_file_path = create_dummy_csv_file(self.evadb.config)

        csv_query = f"""LOAD CSV '{self.csv_file_path}' INTO MyTextCSV;"""
        execute_query_fetch_all(self.evadb, csv_query)

    def tearDown(self) -> None:
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyTextCSV;")

    @chatgpt_skip_marker
    def test_openai_chat_completion_udf(self):
        udf_name = "OpenAIChatCompletion"
        execute_query_fetch_all(self.evadb, f"DROP UDF IF EXISTS {udf_name};")

        create_udf_query = f"""CREATE UDF IF NOT EXISTS{udf_name}
            IMPL 'evadb/udfs/chatgpt.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        gpt_query = f"SELECT {udf_name}('summarize', content) FROM MyTextCSV;"
        output_batch = execute_query_fetch_all(self.evadb, gpt_query)
        self.assertEqual(output_batch.columns, ["openaichatcompletion.response"])

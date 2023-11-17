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
from io import BytesIO
from test.util import get_evadb_for_testing
from typing import List, Optional
from unittest.mock import MagicMock, patch

from PIL import Image as PILImage
from pydantic import AnyUrl, BaseModel

from evadb.server.command_handler import execute_query_fetch_all


class Image(BaseModel):
    b64_json: Optional[str]  # Replace with the actual type if different
    revised_prompt: Optional[str]  # Replace with the actual type if different
    url: AnyUrl


class ImagesResponse(BaseModel):
    created: Optional[int]  # Replace with the actual type if different
    data: List[Image]


class DallEFunctionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        create_table_query = """CREATE TABLE IF NOT EXISTS ImageGen (
             prompt TEXT(100));
                """
        execute_query_fetch_all(self.evadb, create_table_query)

        test_prompts = ["a surreal painting of a cat"]

        for prompt in test_prompts:
            insert_query = f"""INSERT INTO ImageGen (prompt) VALUES ('{prompt}')"""
            execute_query_fetch_all(self.evadb, insert_query)

    def tearDown(self) -> None:
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS ImageGen;")

    @patch.dict("os.environ", {"OPENAI_API_KEY": "mocked_openai_key"})
    @patch("requests.get")
    @patch("openai.OpenAI")
    def test_dalle_image_generation(self, mock_openai, mock_requests_get):
        # Generate a 1x1 white pixel PNG image in memory
        img = PILImage.new("RGB", (1, 1), color="white")
        img_byte_array = BytesIO()
        img.save(img_byte_array, format="PNG")
        mock_image_content = img_byte_array.getvalue()

        mock_response = MagicMock()
        mock_response.content = mock_image_content
        mock_requests_get.return_value = mock_response

        # Set up the mock for OpenAI instance
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.images.generate.return_value = ImagesResponse(
            data=[
                Image(
                    b64_json=None,
                    revised_prompt=None,
                    url="https://images.openai.com/1234.png",
                )
            ]
        )

        function_name = "DallE"

        execute_query_fetch_all(self.evadb, f"DROP FUNCTION IF EXISTS {function_name};")

        create_function_query = f"""CREATE FUNCTION IF NOT EXISTS {function_name}
            IMPL 'evadb/functions/dalle.py';
        """
        execute_query_fetch_all(self.evadb, create_function_query)

        gpt_query = f"SELECT {function_name}(prompt) FROM ImageGen;"
        execute_query_fetch_all(self.evadb, gpt_query)

        mock_openai_instance.images.generate.assert_called_once_with(
            prompt="a surreal painting of a cat", n=1, size="1024x1024"
        )

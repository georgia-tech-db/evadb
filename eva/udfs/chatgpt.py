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


import openai
import pandas as pd

from eva.catalog.catalog_type import NdArrayType
from eva.configuration.configuration_manager import ConfigurationManager
from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.decorators.io_descriptors.data_types import PandasDataframe

_VALID_CHAT_COMPLETION_MODEL = [
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301",
]


class ChatGPT(AbstractUDF):
    @property
    def name(self) -> str:
        return "ChatGPT"

    @setup(cacheable=False, udf_type="chat-completion", batchable=True)
    def setup(
        self,
        model="gpt-3.5-turbo",
        temperature: float = 0,
    ) -> None:
        openai.api_key = ConfigurationManager().get_value(
            "third_party", "openai_api_key"
        )
        assert (
            len(openai.api_key) != 0
        ), "Please set your OpenAI API key in eva.yml file (third_party, open_api_key)"

        assert model in _VALID_CHAT_COMPLETION_MODEL, f"Unsupported ChatGPT {model}"

        self.model = model
        self.temperature = temperature

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["prompt", "query"],
                column_types=[
                    NdArrayType.STR,
                    NdArrayType.STR,
                ],
                column_shapes=[(1,), (1,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["response"],
                column_types=[
                    NdArrayType.STR,
                ],
                column_shapes=[(1,)],
            )
        ],
    )
    def forward(self, text_df):
        prompts = text_df[text_df.columns[0]]
        queries = text_df[text_df.columns[1]]

        # openai api currently supports answers to a single prompt only
        # so this udf is designed such that

        results = []

        for prompt, query in zip(prompts, queries):
            if prompt != "None":
                query = prompt + ": " + query

            params = {
                "model": self.model,
                "temperature": self.temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": query,
                    }
                ],
            }
            response = openai.ChatCompletion.create(**params)
            results.append(response.choices[0].message.content)

        df = pd.DataFrame({"response": results})

        return df

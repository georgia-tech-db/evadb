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


class GPTUdf(AbstractUDF):
    @property
    def name(self) -> str:
        return "chatgpt"

    @setup(cachable=True, udf_type="=text-completion", batchable=True)
    def setup(self) -> None:
        openai.api_key = ConfigurationManager().get_value("core", "openai_api_key")
        assert (
            len(openai.api_key) != 0
        ), "Please set your openai api key in eva.yml file"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["id", "query"],
                column_types=[NdArrayType.ANYTYPE, NdArrayType.ANYTYPE],
                column_shapes=[(None,), (None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["input_query", "responses"],
                column_types=[
                    NdArrayType.ANYTYPE,
                    NdArrayType.ANYTYPE,
                ],
                column_shapes=[(None,), (None,)],
            )
        ],
    )
    def forward(self, text_df):

        result = []
        queries = text_df[text_df.columns[0]]

        for query in queries:
              
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=[{"role": "user", "content": query}]
            )
            
            for choice in response.choices:
                result.append(choice.message.content)
                

        df = pd.DataFrame({"input_query": queries, "responses": result})

        return df

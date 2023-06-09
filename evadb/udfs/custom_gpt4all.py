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


import gpt4all
import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe


class CustomGPT4All(AbstractUDF):
    @property
    def name(self) -> str:
        return "CustomGPT4All"

    @setup(cacheable=False, udf_type="gpt4all", batchable=True)
    def setup(
        self,
        model_name="ggml-gpt4all-j-v1.3-groovy",
        n_ctx=1000,
        n_predict=256,
        temp=0.8,
        top_k=40,
        repeat_last_n=64,
        repeat_penalty=1.3,
        context_erase=0.5,
    ) -> None:
        # Try Configuration Manager

        self.model = gpt4all.GPT4All(model_name=model_name)
        self.generate_args = {
            "n_ctx": n_ctx,
            "n_predict": n_predict,
            "temp": temp,
            "top_k": top_k,
            "repeat_last_n": repeat_last_n,
            "repeat_penalty": repeat_penalty,
            "context_erase": context_erase,
        }

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["prompt"],
                column_types=[
                    NdArrayType.STR,
                ],
                column_shapes=[(1,)],
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
        prompt = text_df.iloc[0, 0]
        response = self.model.generate(prompt, **self.generate_args, streaming=False)
        return pd.DataFrame({"response": [response]})

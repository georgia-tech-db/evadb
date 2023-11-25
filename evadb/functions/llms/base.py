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


import json
import os
from abc import abstractmethod
from typing import List

import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe


class BaseLLM(AbstractFunction):
    """ """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_stats = None

    @setup(cacheable=True, function_type="chat-completion", batchable=True)
    def setup(self, *args, **kwargs) -> None:
        super().setup(*args, **kwargs)

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["query", "content", "prompt"],
                column_types=[
                    NdArrayType.STR,
                    NdArrayType.STR,
                    NdArrayType.STR,
                ],
                column_shapes=[(1,), (1,), (None,)],
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
        queries = text_df[text_df.columns[0]]
        contents = text_df[text_df.columns[0]]
        if len(text_df.columns) > 1:
            queries = text_df.iloc[:, 0]
            contents = text_df.iloc[:, 1]

        prompt = None
        if len(text_df.columns) > 2:
            prompt = text_df.iloc[0, 2]

        responses = self.generate(queries, contents, prompt)
        return pd.DataFrame({"response": responses})

    @abstractmethod
    def generate(self, queries: List[str], contents: List[str], prompt: str) -> List[str]:
        """
        All the child classes should overload this function
        """
        raise NotImplementedError

    @abstractmethod
    def get_cost(self, prompt: str, query: str, content: str, response: str = "") -> tuple(tuple, float):
        """
        Return the token usage as tuple of input_token_usage, output_token_usage, and dollar cost of running the LLM on the prompt and the getting the provided response.
        """
        pass

    @abstractmethod
    def get_max_cost(self, prompt: str, query: str, content: str) -> tuple(tuple, float):
        """
        Return the token usage as tuple of input_token_usage, output_token_usage, and dollar cost of running the LLM on the prompt and the getting the provided response.
        """
        pass

    def get_model_stats(self, model_name: str):
        # read the statistics if not already read
        if self.model_stats is None:
            current_file_path = os.path.dirname(os.path.realpath(__file__))
            with open(f"{current_file_path}/llm_stats.json") as f:
                self.model_stats = json.load(f)

        assert (
            model_name in self.model_stats
        ), f"we do not have statistics for the model {model_name}"

        return self.model_stats[model_name]

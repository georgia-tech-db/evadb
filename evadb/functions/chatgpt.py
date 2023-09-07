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

import pandas as pd
from retry import retry

from evadb.catalog.catalog_type import NdArrayType
from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.utils.generic_utils import try_to_import_litellm

_VALID_CHAT_COMPLETION_MODEL = [
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301",
]


class ChatGPT(AbstractFunction):
    """
    Arguments:
        model (str) : ID of the OpenAI model to use. Refer to '_VALID_CHAT_COMPLETION_MODEL' for a list of supported models.
        temperature (float) : Sampling temperature to use in the model. Higher value results in a more random output.

    Input Signatures:
        query (str)   : The task / question that the user wants the model to accomplish / respond.
        content (str) : Any relevant context that the model can use to complete its tasks and generate the response.
        prompt (str)  : An optional prompt that can be passed to the model. It can contain instructions to the model,
                        or a set of examples to help the model generate a better response.
                        If not provided, the system prompt defaults to that of an helpful assistant that accomplishes user tasks.

    Output Signatures:
        response (str) : Contains the response generated by the model based on user input. Any errors encountered
                         will also be passed in the response.

    Example Usage:
        Assume we have the transcripts for a few videos stored in a table 'video_transcripts' in a column named 'text'.
        If the user wants to retrieve the summary of each video, the ChatGPT function can be used as:

            query = "Generate the summary of the video"
            cursor.table("video_transcripts").select(f"ChatGPT({query}, text)")

        In the above function invocation, the 'query' passed would be the user task to generate video summaries, and the
        'content' passed would be the video transcripts that need to be used in order to generate the summary. Since
        no prompt is passed, the default system prompt will be used.

        Now assume the user wants to create the video summary in 50 words and in French. Instead of passing these instructions
        along with each query, a prompt can be set as such:

            prompt = "Generate your responses in 50 words or less. Also, generate the response in French."
            cursor.table("video_transcripts").select(f"ChatGPT({query}, text, {prompt})")

        In the above invocation, an additional argument is passed as prompt. While the query and content arguments remain
        the same, the 'prompt' argument will be set as a system message in model params.

        Both of the above cases would generate a summary for each row / video transcript of the table in the response.
    """

    @property
    def name(self) -> str:
        return "ChatGPT"

    @setup(cacheable=False, function_type="chat-completion", batchable=True)
    def setup(
        self,
        model="gpt-3.5-turbo",
        temperature: float = 0,
    ) -> None:
        assert model in _VALID_CHAT_COMPLETION_MODEL, f"Unsupported ChatGPT {model}"
        self.model = model
        self.temperature = temperature

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
        try_to_import_litellm()
        import litellm

        @retry(tries=6, delay=20)
        def completion_with_backoff(**kwargs):
            return litellm.completion(**kwargs)

        # Register API key, try configuration manager first
        litellm.api_key = ConfigurationManager().get_value("third_party", "OPENAI_KEY")
        # If not found, try OS Environment Variable
        if len(litellm.api_key) == 0:
            litellm.api_key = os.environ.get("OPENAI_KEY", "")
        assert (
            len(litellm.api_key) != 0
        ), "Please set your OpenAI API key in evadb.yml file (third_party, open_api_key) or environment variable (OPENAI_KEY)"

        queries = text_df[text_df.columns[0]]
        content = text_df[text_df.columns[0]]
        if len(text_df.columns) > 1:
            queries = text_df.iloc[:, 0]
            content = text_df.iloc[:, 1]

        prompt = None
        if len(text_df.columns) > 2:
            prompt = text_df.iloc[0, 2]

        # openai api currently supports answers to a single prompt only
        # so this function is designed for that
        results = []

        for query, content in zip(queries, content):
            params = {
                "model": self.model,
                "temperature": self.temperature,
                "messages": [],
            }

            def_sys_prompt_message = {
                "role": "system",
                "content": prompt
                if prompt is not None
                else "You are a helpful assistant that accomplishes user tasks.",
            }

            params["messages"].append(def_sys_prompt_message)
            params["messages"].extend(
                [
                    {
                        "role": "user",
                        "content": f"Here is some context : {content}",
                    },
                    {
                        "role": "user",
                        "content": f"Complete the following task: {query}",
                    },
                ],
            )

            response = completion_with_backoff(**params)
            answer = response.choices[0].message.content
            results.append(answer)

        df = pd.DataFrame({"response": results})

        return df

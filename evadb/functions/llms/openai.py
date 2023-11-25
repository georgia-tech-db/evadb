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
from typing import List

from retry import retry

from evadb.functions.llms.base import BaseLLM
from evadb.utils.generic_utils import (
    try_to_import_openai,
    try_to_import_tiktoken,
    validate_kwargs,
)

_VALID_MODELs = [
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301",
]
_DEFAULT_PARAMS = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.0,
    "request_timeout": 30,
    "max_tokens": 1000,
    "messages": [],
}


class OpenAILLM(BaseLLM):
    @property
    def name(self) -> str:
        return "OpenAILLM"

    def setup(
        self,
        openai_api_key="",
        **kwargs,
    ) -> None:
        super().setup(**kwargs)

        try_to_import_openai()
        import openai

        openai.api_key = openai_api_key
        if len(openai.api_key) == 0:
            openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        assert (
            len(openai.api_key) != 0
        ), "Please set your OpenAI API key using SET OPENAI_API_KEY = 'sk-' or environment variable (OPENAI_API_KEY)"

        validate_kwargs(kwargs, allowed_keys=_DEFAULT_PARAMS.keys(), required_keys=[])
        self.model_params = {**_DEFAULT_PARAMS, **kwargs}

        self.model_name = self.model_params["model"]

    def generate(self, queries: List[str], contents: List[str], prompt: str) -> List[str]:
        import openai

        @retry(tries=6, delay=20)
        def completion_with_backoff(**kwargs):
            return openai.ChatCompletion.create(**kwargs)

        results = []

        for query, content in zip(queries, contents):
            def_sys_prompt_message = {
                "role": "system",
                "content": prompt
                if prompt is not None
                else "You are a helpful assistant that accomplishes user tasks.",
            }

            self.model_params["messages"].append(def_sys_prompt_message)
            self.model_params["messages"].extend(
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

            response = completion_with_backoff(**self.model_params)
            answer = response.choices[0].message.content
            results.append(answer)

        return results

    def get_cost(self, prompt: str, query: str, content: str, response: str):
        try_to_import_tiktoken()
        import tiktoken

        encoding = tiktoken.encoding_for_model(self.model_name)
        num_prompt_tokens = len(encoding.encode(prompt))
        num_query_tokens = len(encoding.encode(query))
        num_content_tokens = len(encoding.encode(content))
        num_response_tokens = self.model_params["max_tokens"]
        if response is not None:
            num_response_tokens = len(encoding.encode(response))

        model_stats = self.get_model_stats(self.model_name)

        token_consumed = (num_prompt_tokens+num_query_tokens+num_content_tokens, num_response_tokens)
        dollar_cost = (
            model_stats["input_cost_per_token"] * token_consumed[0]
            + model_stats["output_cost_per_token"] * token_consumed[1]
        )
        return token_consumed, dollar_cost
    
    def get_max_cost(self, prompt: str, query: str, content: str):
        return self.get_cost(prompt, query, content, response=None)

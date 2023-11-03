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
from io import BytesIO

import numpy as np
import pandas as pd
import json
from retry import retry

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.utils.generic_utils import try_to_import_openai
from evadb.utils.logging_manager import logger


class ExtractColumnsFunction(AbstractFunction):
    @property
    def name(self) -> str:
        return "EXTRACT_COLUMNS"

    def setup(
        self, 
        model="gpt-3.5-turbo",
        temperature: float = 0,
        openai_api_key=""
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.openai_api_key = openai_api_key

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["input_rows"],
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
    def forward(self, unstructured_df):
        """
        NOTE (QUESTION) : Can we structure the inputs and outputs better
        The circumvent issues surrounding the input being only one pandas dataframe and output columns being predefined 
        Will add all column types as a JSON and parse in the forward function
        Provide only the file name from which the input will be read
        Output in JSON which can be serialized and stored in the results column of the DF
        """
        
        try_to_import_openai()
        import openai
        
        @retry(tries=6, delay=20)
        def completion_with_backoff(**kwargs):
            return openai.ChatCompletion.create(**kwargs)

        openai.api_key = self.openai_api_key
        # If not found, try OS Environment Variable
        if len(openai.api_key) == 0:
            openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        assert (
            len(openai.api_key) != 0
        ), "Please set your OpenAI API key using SET OPENAI_API_KEY = 'sk-'  or environment variable (OPENAI_API_KEY)"

        def generate_structured_data(unstructured_df: PandasDataframe):
            results = []
            #column_types = json.loads(unstructured_df[unstructured_df.columns[0]])
            input_rows = unstructured_df[unstructured_df.columns[0]]
            
            column_types_dict = {
                "columns":
                [
                    {
                        "name": "Issue Category",
                        "description": "The category of the issue",
                        "type": "One of (hardware, software)"
                    },
                    {
                        "name": "Raw Issue String",
                        "description": "The raw issue string containing the exact input given by the user",
                        "type": "string"
                    },
                    {
                        "name": "Issue Component",
                        "description": "The component that is causing the issue",
                        "type": "string"
                    },
                ]
            }
            
            column_types = json.dumps(column_types_dict)
            
            base_prompt = """
            You are given a user query. Your task is to extract the following fields from the query and return the result in json format.\n
            """
            
            # TODO : Check if this is fine or if we need to add column types as string
            """
            Not able to add serialized json as input to the column types. Adding a static column types list for now
            """
            
            for input_row in input_rows:
                # TODO : Hardcoding some params for now, will revert later
                params = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": [],
                }

                def_sys_prompt_message = {
                    "role": "system",
                    "content": base_prompt
                }

                params["messages"].append(def_sys_prompt_message)
                params["messages"].extend(
                    [
                        {
                            "role": "user",
                            "content": f"Here are the column types we need the data to be structured in : \n {column_types} \n",
                        },
                        {
                            "role": "user",
                            "content": f"Here is the unstructured query which needs to be converted: {input_row}\n",
                        },
                    ],
                )
                
                logger.info("Params {}".format(params))
                response = completion_with_backoff(**params)
                
                logger.info("Response {}".format(response))
                answer = response.choices[0].message.content
                results.append(answer)
                

            return results

        df = pd.DataFrame({"response": generate_structured_data(unstructured_df=unstructured_df)})
        return df

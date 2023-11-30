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

import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.chatgpt import ChatGPT
from evadb.functions.decorators.decorators import forward
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe


class ExtractColumnFunction(ChatGPT):
    @property
    def name(self) -> str:
        return "EXTRACT_COLUMN"

    def setup(
        self, model="gpt-3.5-turbo", temperature: float = 0, openai_api_key=""
    ) -> None:
        super(ExtractColumnFunction, self).setup(model, temperature, openai_api_key)

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["field_name", "description", "data_type", "input_rows"],
                column_types=[
                    NdArrayType.STR,
                    NdArrayType.STR,
                    NdArrayType.STR,
                    NdArrayType.STR,
                ],
                column_shapes=[
                    (1,),
                    (1,),
                    (1,),
                    (1,),
                ],
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
        field_name = unstructured_df.iloc[0, 0]
        description = unstructured_df.iloc[0, 1]
        data_type = unstructured_df.iloc[0, 2]
        input_rows = unstructured_df[unstructured_df.columns[3]]
        prompt = """
            You are given a user query. Your task is to extract the following fields from the query and return the result in string format.
            IMPORTANT: RETURN ONLY THE EXTRACTED VALUE (one word or phrase). DO NOT RETURN THE FIELD NAME OR ANY OTHER INFORMATION.
        """
        content = """
            Extract the following fields from the unstructured text below:
            Format of the field is given in the format
            Field Name: Field Description: Field Type
            {}: {}: {}
            The unstructured text is as follows:
        """.format(
            field_name, description, data_type
        )

        output_df = pd.DataFrame({"response": []})

        for row in input_rows:
            query = row
            input_df = pd.DataFrame(
                {"query": [query], "content": content, "prompt": prompt}
            )
            df = super(ExtractColumnFunction, self).forward(input_df)
            output_df = pd.concat([output_df, df], ignore_index=True)
        return output_df

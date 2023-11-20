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
import requests
from PIL import Image

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.utils.generic_utils import try_to_import_openai


class DallEFunction(AbstractFunction):
    @property
    def name(self) -> str:
        return "DallE"

    def setup(self, openai_api_key="") -> None:
        self.openai_api_key = openai_api_key

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["prompt"],
                column_types=[
                    NdArrayType.STR,
                ],
                column_shapes=[(None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["response"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
            )
        ],
    )
    def forward(self, text_df):
        try_to_import_openai()
        from openai import OpenAI

        api_key = self.openai_api_key
        if len(self.openai_api_key) == 0:
            api_key = os.environ.get("OPENAI_API_KEY", "")
        assert (
            len(api_key) != 0
        ), "Please set your OpenAI API key using SET OPENAI_API_KEY = 'sk-' or environment variable (OPENAI_API_KEY)"

        client = OpenAI(api_key=api_key)

        def generate_image(text_df: PandasDataframe):
            results = []
            queries = text_df[text_df.columns[0]]
            for query in queries:
                response = client.images.generate(prompt=query, n=1, size="1024x1024")

                # Download the image from the link
                image_response = requests.get(response.data[0].url)
                image = Image.open(BytesIO(image_response.content))

                # Convert the image to an array format suitable for the DataFrame
                frame = np.array(image)
                results.append(frame)

            return results

        df = pd.DataFrame({"response": generate_image(text_df=text_df)})
        return df

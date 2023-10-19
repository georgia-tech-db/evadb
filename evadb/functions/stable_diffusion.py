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
from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.utils.generic_utils import try_to_import_replicate


class StableDiffusion(AbstractFunction):
    @property
    def name(self) -> str:
        return "StableDiffusion"

    def setup(
        self,
    ) -> None:
        pass

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
                column_types=[
                    # FileFormatType.IMAGE,
                    NdArrayType.FLOAT32
                ],
                column_shapes=[(None, None, 3)],
            )
        ],
    )
    def forward(self, text_df):
        try_to_import_replicate()
        import replicate

        # Register API key, try configuration manager first
        replicate_api_key = ConfigurationManager().get_value(
            "third_party", "REPLICATE_API_TOKEN"
        )
        # If not found, try OS Environment Variable
        if replicate_api_key is None:
            replicate_api_key = os.environ.get("REPLICATE_API_TOKEN", "")
        assert (
            len(replicate_api_key) != 0
        ), "Please set your Replicate API key in evadb.yml file (third_party, replicate_api_token) or environment variable (REPLICATE_API_TOKEN)"
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_key

        model_id = (
            replicate.models.get("stability-ai/stable-diffusion").versions.list()[0].id
        )

        def generate_image(text_df: PandasDataframe):
            results = []
            queries = text_df[text_df.columns[0]]
            for query in queries:
                output = replicate.run(
                    "stability-ai/stable-diffusion:" + model_id, input={"prompt": query}
                )

                # Download the image from the link
                response = requests.get(output[0])
                image = Image.open(BytesIO(response.content))

                # Convert the image to an array format suitable for the DataFrame
                frame = np.array(image)
                results.append(frame)

            return results

        df = pd.DataFrame({"response": generate_image(text_df=text_df)})
        return df

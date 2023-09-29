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

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.utils.generic_utils import try_to_import_replicate

_VALID_STABLE_DIFFUSION_MODEL = [
    "sdxl:af1a68a271597604546c09c64aabcd7782c114a63539a4a8d14d1eeda5630c33",
]


class StableDiffusion(AbstractFunction):
    @property
    def name(self) -> str:
        return "StableDiffusion"

    def setup(
        self,
        model="sdxl:af1a68a271597604546c09c64aabcd7782c114a63539a4a8d14d1eeda5630c33",
    ) -> None:
        assert (
            model in _VALID_STABLE_DIFFUSION_MODEL
        ), f"Unsupported Stable Diffusion {model}"
        self.model = model

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
                    NdArrayType.STR,
                ],
                column_shapes=[(1,)],
            )
        ],
    )
    def forward(self, text_df):
        try_to_import_replicate()
        import replicate

        if os.environ.get("REPLICATE_API_TOKEN") is None:
            replicate_api_key = (
                "r8_Q75IAgbaHFvYVfLSMGmjQPcW5uZZoXz0jGalu"  # token for testing
            )
            os.environ["REPLICATE_API_TOKEN"] = replicate_api_key

        # @retry(tries=5, delay=20)
        def generate_image(text_df: PandasDataframe):
            results = []
            queries = text_df[text_df.columns[0]]
            for query in queries:
                output = replicate.run(
                    "stability-ai/" + self.model, input={"prompt": query}
                )
                results.append(output[0])
            return results

        df = pd.DataFrame({"response": generate_image(text_df=text_df)})

        return df

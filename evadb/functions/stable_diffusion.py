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

from evadb.utils.generic_utils import try_to_import_replicate
import os

import pandas as pd
from retry import retry

from evadb.catalog.catalog_type import NdArrayType
from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe


_VALID_STABLE_DIFFUSION_MODEL = [
    "stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
]

class StableDiffusion(AbstractFunction):
    @property
    def name(self) -> str:
        return "StableDiffusion"

    @setup(cacheable=False, function_type="image-generation", batchable=True)
    def setup(
        self,
        model="stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478"
    ) -> None:
        assert model in _VALID_STABLE_DIFFUSION_MODEL, f"Unsupported Stable Diffusion {model}"
        self.model = model

    @forward(
        input_signatures=[
            PandasDataframe(
                columns = ["prompt"],
                column_types=[
                    NdArrayType.STR,
                ],
                column_shapes=[(1,)]
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

        replicate_api_key = ConfigurationManager().get_value("third_party", "REPLICATE_API_TOKEN")
        if len(replicate_api_key) == 0:
            replicate_api_key = os.environ.get("REPLICATE_API_TOKEN", "")

        assert(
            len(replicate_api_key) != 0
        ), "Please set your Replicate API Token as environment variable (REPLICATE_API_TOKEN)"
        
        
        
        @retry(tries=5, delay=20)
        def generate_image(text_df : PandasDataframe):
            results = []
            queries = text_df[text_df.columns[0]]
            for query in queries:
                output = replicate.run(
                    "stability-ai/" + self.model,
                    input={"prompt": query}
                )
                results.append(output)
            return results

        df = pd.DataFrame({"response":generate_image(text_df=text_df)})

        return df
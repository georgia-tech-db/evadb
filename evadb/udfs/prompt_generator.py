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
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe

prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:"""


class PromptGenerator(AbstractUDF):
    @setup(cacheable=False, udf_type="PromptGeneration", batchable=False)
    def setup(self):
        pass

    @property
    def name(self) -> str:
        return "PromptGenerator"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data", "question"],
                column_types=[NdArrayType.STR, NdArrayType.STR],
                column_shapes=[(None, 1), (None, 1)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["prompt"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None, 1)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        # By default assume first column has data, but we don't know name of column
        context = "\n\n".join(df.iloc[:, 0].tolist())
        question = df.iloc[:, 1].tolist()[0]
        prompt = prompt_template.format(context=context, question=question)
        return pd.DataFrame({"prompt": [prompt]})

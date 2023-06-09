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
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

from evadb.catalog.catalog_type import NdArrayType
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe
from evadb.udfs.gpu_compatible import GPUCompatible


class SentenceFeatureExtractor(AbstractUDF, GPUCompatible):
    @setup(cacheable=False, udf_type="FeatureExtraction", batchable=False)
    def setup(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    def to_device(self, device: str) -> GPUCompatible:
        self.model_device = device
        self.model = self.model.to(device)
        return self

    @property
    def name(self) -> str:
        return "SentenceFeatureExtractor"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None, 1)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["features"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(1, 384)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        def _forward(row: pd.Series) -> np.ndarray:
            sentence = row[0]

            encoded_input = self.tokenizer(
                [sentence], padding=True, truncation=True, return_tensors="pt"
            )
            encoded_input.to(self.model_device)
            with torch.no_grad():
                model_output = self.model(**encoded_input)

            attention_mask = encoded_input["attention_mask"]
            token_embedding = model_output[0]
            input_mask_expanded = (
                attention_mask.unsqueeze(-1).expand(token_embedding.size()).float()
            )
            sentence_embedding = torch.sum(
                token_embedding * input_mask_expanded, 1
            ) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            sentence_embedding = F.normalize(sentence_embedding, p=2, dim=1)

            sentence_embedding_np = sentence_embedding.cpu().numpy()
            return sentence_embedding_np

        ret = pd.DataFrame()
        ret["features"] = df.apply(_forward, axis=1)
        return ret


# coding=utf-8
# Copyright 2018-2022 EVA
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
import cv2
import kornia
import numpy as np
import pandas as pd
import torch
import torchvision
import torch.nn as nn
import torch.nn.functional as F

from eva.catalog.catalog_type import NdArrayType
from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.decorators.io_descriptors.data_types import PandasDataframe
from eva.udfs.gpu_compatible import GPUCompatible
from torchvision.transforms import Compose, ToTensor, Resize
from PIL import Image

import spacy
try:
    nlp = spacy.load("en_core_web_lg")
except:
    import spacy.cli
    spacy.cli.download("en_core_web_lg")
    nlp = spacy.load("en_core_web_lg")


class SimilarityFeatureExtractor(AbstractUDF, GPUCompatible):
    @setup(cacheable=False, udf_type="FeatureExtraction", batchable=False)
    def setup(self):
        pass

    def to_device(self, device: str) -> GPUCompatible:
        self.model = self.model.to(device)
        return self

    @property
    def name(self) -> str:
        return "SimilarityFeatureExtractor"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data","filter"],
                column_types=[NdArrayType.STR,NdArrayType.STR],
                column_shapes=[(1),(1)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["simiarity"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(1)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:

        def _forward(row: pd.Series) -> np.ndarray:
            columns=row.axes[0]
            data = row.loc[columns[0]]
            filter_keyword = row.loc[columns[1]]
            if data.strip()!="":
                doc1 = nlp(data)
                doc2 = nlp(filter_keyword)
                return doc1.similarity(doc2)
            else:
                return 0

        ret = pd.DataFrame()
        ret["simiarity"] = df.apply(_forward, axis=1)
        return ret

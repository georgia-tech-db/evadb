
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


class SaliencyFeatureExtractor(AbstractUDF, GPUCompatible):
    @setup(cacheable=False, udf_type="FeatureExtraction", batchable=False)
    def setup(self):
        # # self.model = kornia.feature.SIFTDescriptor(100)
        # self.model = torchvision.models.resnet18(pretrained=True)
        # num_features = self.model.fc.in_features
        # self.model.fc = nn.Linear(num_features, 2) # binary classification (num_of_class == 2)
        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # model_state = torch.load("data/saliency/model.pth", map_location=device)
        # self.model.load_state_dict(model_state)
        # self.model.eval()
        pass

    def to_device(self, device: str) -> GPUCompatible:
        self.model = self.model.to(device)
        return self

    @property
    def name(self) -> str:
        return "SaliencyFeatureExtractor"

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
                columns=["saliency"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(1, 224,224)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        def _forward(row: pd.Series) -> np.ndarray:
            columns=row.axes[0]
            res = row.loc[columns[1]]
            return res

        ret = pd.DataFrame()
        ret["saliency"] = df.apply(_forward, axis=1)
        return ret

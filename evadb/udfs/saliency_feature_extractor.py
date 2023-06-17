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
import torchvision
from PIL import Image
from torchvision.transforms import Compose, Resize, ToTensor

from evadb.catalog.catalog_type import NdArrayType
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe
from evadb.udfs.gpu_compatible import GPUCompatible


class SaliencyFeatureExtractor(AbstractUDF, GPUCompatible):
    @setup(cacheable=False, udf_type="FeatureExtraction", batchable=False)
    def setup(self):
        self.model = torchvision.models.resnet18(pretrained=True)
        self.model.eval()

    def to_device(self, device: str) -> GPUCompatible:
        self.model = self.model.to(device)
        return self

    @property
    def name(self) -> str:
        return "SaliencyFeatureExtractor"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.UINT8],
                column_shapes=[(None, None, 3)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["saliency"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(1, 224, 224)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        def _forward(row: pd.Series) -> np.ndarray:
            rgb_img = row[0]

            composed = Compose([Resize((224, 224)), ToTensor()])
            transformed_img = composed(Image.fromarray(rgb_img[:, :, ::-1])).unsqueeze(
                0
            )
            transformed_img.requires_grad_()
            outputs = self.model(transformed_img)
            score_max_index = outputs.argmax()
            score_max = outputs[0, score_max_index]
            score_max.backward()
            saliency, _ = torch.max(transformed_img.grad.data.abs(), dim=1)

            return saliency

        ret = pd.DataFrame()
        ret["saliency"] = df.apply(_forward, axis=1)
        return ret

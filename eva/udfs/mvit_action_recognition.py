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

import numpy as np
import pandas as pd
import torch
from torchvision.models.video import MViT_V2_S_Weights, mvit_v2_s

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF


class MVITActionRecognition(PytorchAbstractClassifierUDF):
    @property
    def name(self) -> str:
        return "MVITActionRecognition"

    def setup(self):
        self.weights = MViT_V2_S_Weights.DEFAULT
        self.model = mvit_v2_s(weights=self.weights)
        self.preprocess = self.weights.transforms()
        self.model.eval()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> np.array([str]):
        return np.array(self.weights.meta["categories"])

    def forward(self, segments):
        return self.classify(segments)

    def transform(self, segments) -> torch.Tensor:
        segments = torch.Tensor(segments)
        segments = segments.permute(0, 3, 1, 2)
        return self.preprocess(segments).unsqueeze(0)

    def classify(self, segments: torch.Tensor) -> pd.DataFrame:
        with torch.no_grad():
            preds = self.model(segments).softmax(1)
        label_indices = preds.argmax(axis=1)
        actions = self.labels[label_indices]
        # TODO ACTION: In the current pipeline, actions will always get batches on
        # length 1, so this case would never be invoked.
        if np.isscalar(actions) == 1:
            outcome = pd.DataFrame({"labels": np.array([actions])})
        return outcome

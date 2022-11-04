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

import pandas as pd
import numpy as np
import torch
from torchvision.models.video import mvit_v2_s, MViT_V2_S_Weights


from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace


class MVITActionRecognition(PytorchAbstractClassifierUDF):

    @property
    def name(self) -> str:
        return 'MVITActionRecognition'

    def setup(self):
        self.weights = MViT_V2_S_Weights.DEFAULT
        self.model = mvit_v2_s(weights=self.weights)
        self.preprocess = self.weights.transforms()
        self.category_names = np.array(self.weights.meta["categories"])
        self.model.eval()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self):
        return list([str(num) for num in range(400)])

    def forward(self, segments):
        return self.classify(segments)

    def transform(self, segments) -> torch.Tensor:
        segments = torch.Tensor(segments)
        segments = segments.permute(0, 3, 1, 2)
        return self.preprocess(segments).unsqueeze(0)

    def classify(self, segments: torch.Tensor) -> pd.DataFrame:
        with torch.no_grad():
            preds = self.model(segments).softmax(1)
        labels = preds.argmax(axis=1)
        scores = preds.gather(1, labels.unsqueeze(0)).squeeze().cpu().numpy()
        actions = self.category_names[labels]
        print(f"{actions}: {100 * scores}%")
        # If batch size is 1
        if np.isscalar(actions) == 1:
            outcome = pd.DataFrame(
                {"labels": np.array([actions])})
        else:
            # TODO ACTION: In the current pipeline, actions will always get batches on
            # length 1, so this case would never be invoked.
            outcome = pd.DataFrame({"labels": actions})
        return outcome

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

import os
import pickle as pkl

import numpy as np
import pandas as pd
import torch
import torchvision

try:
    from torchvision.models.video import R3D_18_Weights, r3d_18

except ImportError:
    raise ImportError(
        f"torchvision>=0.14.0 is required to use video_resnet, found {torchvision.__version__}"
    )
import torch.nn as nn
import torchvision

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF


class ASLActionRecognition(PytorchAbstractClassifierUDF):
    @property
    def name(self) -> str:
        return "ASLActionRecognition"

    def download_weights(self):
        if not os.path.exists(self.asl_weights_path):
            torch.hub.download_url_to_file(
                self.asl_weights_url,
                self.asl_weights_path,
                hash_prefix=None,
                progress=True,
            )

    def setup(self):
        self.asl_weights_url = (
            "https://gatech.box.com/shared/static/crjhyy4nc2i5nayesfljutwc1y3bpw2q.pth"
        )
        self.asl_weights_path = torch.hub.get_dir() + "/asl_weights.pth"
        self.download_weights()

        self.weights = R3D_18_Weights.DEFAULT
        self.model = r3d_18(weights=self.weights)
        in_feats = self.model.fc.in_features
        self.model.fc = nn.Linear(in_feats, 20)
        self.model.load_state_dict(
            torch.load(self.asl_weights_path, map_location="cpu")
        )
        self.model.eval()

        self.preprocess = self.weights.transforms()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> np.array([str]):
        with open("asl_20_actions_map.pkl", "rb") as f:
            action_to_index_map = pkl.load(f)
        actions_arr = [""] * len(action_to_index_map)
        for action, index in action_to_index_map.items():
            actions_arr[index] = action
        return np.asarray(actions_arr)

    def forward(self, segments):
        return self.classify(segments)

    def transform(self, segments) -> torch.Tensor:
        segments = torch.Tensor(segments)
        permute_order = [2, 1, 0]
        segments = segments[:, :, :, permute_order]
        segments = segments.permute(0, 3, 1, 2).to(torch.uint8)
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

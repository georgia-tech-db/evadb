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

from typing import List

import pandas as pd
import torch
from torch import Tensor
import torchvision
from torchvision import models
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF


class FeatureExtractor(PytorchAbstractClassifierUDF):
    """ """

    def setup(self):
        if torchvision.__version__ < "0.13.0":
            self.model = models.resnet50(pretrained=True, progress=False)
        else:
            self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

        for param in self.model.parameters():
            param.requires_grad = False
        self.model.fc = torch.nn.Identity()
        self.model.eval()

    @property
    def name(self) -> str:
        return "FeatureExtractor"

    @property
    def labels(self) -> List[str]:
        return []

    def forward(self, frames: Tensor) -> pd.DataFrame:
        """
        Performs feature extraction on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed

        Returns:
            features (List[float])
        """


        # outcome = pd.DataFrame()
        # for f in frames:
        #     with torch.no_grad():
        #         feature_vector = self.as_numpy(self.model(torch.unsqueeze(f, 0)))
        #         outcome = outcome.append(
        #             {"features": feature_vector},
        #             ignore_index=True,
        #         )
        #return outcome


        outcome_list = []
        for f in frames:
            with torch.no_grad():
                feature_vector = self.as_numpy(self.model(torch.unsqueeze(f, 0)))
                df = pd.DataFrame(columns=['features'])
                df.loc[0] = [feature_vector]
                outcome_list.append(df)
        outcome2 = pd.concat(outcome_list, ignore_index=True)
        # assert(outcome2.equals(outcome))
        return outcome2

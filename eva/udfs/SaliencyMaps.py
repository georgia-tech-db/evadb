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
import numpy as np
import pandas as pd

from typing import List

##############
import pandas as pd
import numpy as np
import os
import torchvision
import torch
import torch.nn as nn
import torch.nn.functional as F


from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
from torch import Tensor
from torchvision import models
from torchvision.transforms import Compose, ToTensor, Resize, ToPILImage
from PIL import Image

##################

from eva.catalog.catalog_type import NdArrayType
from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.decorators.io_descriptors.data_types import PandasDataframe,PyTorchTensor


class SaliencyMaps(AbstractUDF):
    @setup(cacheable=False, udf_type="Classification", batchable=True)
    def setup(self):
        self.model = torchvision.models.resnet18(pretrained=True)
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, 2) # binary classification (num_of_class == 2)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_state = torch.load("data/saliency/model.pth", map_location=device)
        self.model.load_state_dict(model_state)
        self.model.eval()

    @property
    def name(self):
        return "SaliencyMaps"

    @forward(
        input_signatures=[
          PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
            )
      ],
        output_signatures=[
            PandasDataframe(
                columns=["saliency"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
            )
        ],
    )
    def forward(self, frames: pd.DataFrame) -> pd.DataFrame:
        """
        Apply Gaussian Blur to the frame

         Returns:
             ret (pd.DataFrame): The modified frame.
        """
        
        outcome = pd.DataFrame(columns=["saliency"])
        frame_np = np.expand_dims(frames["saliency.data"][0],axis=0)
        
        frames_tensor = torch.tensor(frame_np).float()
        frames_tensor.requires_grad_()
        frames_shape = frames_tensor.size()
        outputs = self.model(frames_tensor)
        score_max_index = outputs.argmax()
        score_max = outputs[0,score_max_index]
        score_max.backward()
        saliency, _ = torch.max(frames_tensor.grad.data.abs(),dim=1)

        outcome.loc[len(outcome.index)] = [saliency]
        return outcome
from typing import List

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
from torchvision.transforms import Compose, ToTensor, Resize
from PIL import Image


class MRICNN(PytorchAbstractClassifierUDF):

    @property
    def name(self) -> str:
        return "MRICNN"

    def setup(self):
        # !wget -nc "https://www.dropbox.com/s/cnsgyitrtw40lgs/model.pth?dl=0" 
        # to get the model from the dropbox
        self.model = torchvision.models.resnet18(pretrained=True)
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, 2) # binary classification (num_of_class == 2)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_state = torch.load("model.pth", map_location=device)
        self.model.load_state_dict(model_state)
        self.model.eval()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return [
            '0', '1'
        ]

    def transform(self, images) -> Compose:
        composed = Compose([
            Resize((224, 224)),            
            ToTensor()
        ])
        # reverse the channels from opencv
        return composed(Image.fromarray(images[:, :, ::-1])).unsqueeze(0)

    def forward(self, frames: Tensor) -> pd.DataFrame:
            """
            Performs predictions on input frames
            Arguments:
                frames (np.ndarray): Frames on which predictions need
                to be performed

            Returns:
                tuple containing predicted_classes (List[str])
            """
            outcome = pd.DataFrame()
            frames.requires_grad_()
            outputs = self.model(frames)
            score_max_index = outputs.argmax()
            score_max = outputs[0,score_max_index]
            score_max.backward()
            saliency, _ = torch.max(frames.grad.data.abs(),dim=1)

            outcome = outcome.append({"saliency" : saliency}, ignore_index=True)        

            return outcome

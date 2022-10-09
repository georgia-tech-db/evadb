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
import subprocess
from typing import List

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch import Tensor
from torchvision import transforms

from eva.configuration.constants import EVA_DEFAULT_DIR
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF

# VGG configuration
cfg = {
    "VGG19": [
        64,
        64,
        "M",
        128,
        128,
        "M",
        256,
        256,
        256,
        256,
        "M",
        512,
        512,
        512,
        512,
        "M",
        512,
        512,
        512,
        512,
        "M",
    ],
}


# helper class for VGG
class VGG(nn.Module):
    def __init__(self, vgg_name):
        super(VGG, self).__init__()
        self.features = self._make_layers(cfg[vgg_name])
        self.classifier = nn.Linear(512, 7)

    def forward(self, x):
        out = self.features(x)
        out = out.view(out.size(0), -1)
        out = F.dropout(out, p=0.5, training=self.training)
        out = self.classifier(out)
        return out

    def _make_layers(self, cfg):
        layers = []
        in_channels = 3
        for x in cfg:
            if x == "M":
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                layers += [
                    nn.Conv2d(in_channels, x, kernel_size=3, padding=1),
                    nn.BatchNorm2d(x),
                    nn.ReLU(inplace=True),
                ]
                in_channels = x
        layers += [nn.AvgPool2d(kernel_size=1, stride=1)]
        return nn.Sequential(*layers)


class EmotionDetector(PytorchAbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "EmotionDetector"

    def setup(self, threshold=0.85):
        self.threshold = threshold

        # load model
        self.model = VGG("VGG19")
        output_directory = os.path.join(EVA_DEFAULT_DIR, "udfs", "models")
        model_path = os.path.join(output_directory, "emotion_detector.t7")

        # pull model from dropbox if not present
        if not os.path.exists(model_path):
            model_url = "https://www.dropbox.com/s/bqblykok62d28mn/emotion_detector.t7"
            subprocess.run(["wget", model_url, "--directory-prefix", output_directory])

        # self.get_device() infers device from the loaded model, so not using it
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_state = torch.load(model_path, map_location=device)
        self.model.load_state_dict(model_state["net"])
        self.model.eval()

        # for augmentation
        self.cut_size = 44

    def transforms_ed(self, frame: Image) -> Tensor:
        """
        Performs augmentation on input frame
        Arguments:
            frame (Tensor): Frame on which augmentation needs
            to be performed
        Returns:
            frame (Tensor): Augmented frame
        """

        # convert to grayscale, resize and make tensor
        frame = frame.convert("L")
        frame = transforms.functional.resize(frame, (48, 48))
        frame = transforms.functional.to_tensor(frame)

        return frame

    def transform(self, images: np.ndarray):
        # reverse the channels from opencv
        return self.transforms_ed(Image.fromarray(images[:, :, ::-1]))

    @property
    def labels(self) -> List[str]:
        return ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

    def forward(self, frames: Tensor) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (Tensor): Frames on which predictions need
            to be performed
        Returns:
            outcome (pd.DataFrame): Emotion Predictions for input frames
        """

        # result dataframe
        outcome = pd.DataFrame()

        # convert to 3 channels, ten crop and stack
        frames = frames.repeat(3, 1, 1)
        frames = transforms.functional.ten_crop(frames, self.cut_size)
        frames = torch.stack([crop for crop in frames])

        # perform predictions and take mean over crops
        predictions = self.model(frames)
        predictions = torch.mean(predictions, dim=0)

        # get the scores
        score = F.softmax(predictions, dim=0)
        _, predicted = torch.max(predictions.data, 0)

        # save results
        outcome = outcome.append(
            {
                "labels": self.labels[predicted.item()],
                "scores": score.cpu().detach().numpy()[predicted.item()],
            },
            ignore_index=True,
        )

        return outcome

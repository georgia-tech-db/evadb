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

import os
from typing import List

import numpy as np
import pandas as pd

from evadb.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
from evadb.utils.generic_utils import (
    try_to_import_pillow,
    try_to_import_torch,
    try_to_import_torchvision,
)

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


class EmotionDetector(PytorchAbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "EmotionDetector"

    def _download_weights(self, weights_url, weights_path):
        import torch

        if not os.path.exists(weights_path):
            torch.hub.download_url_to_file(
                weights_url,
                weights_path,
                hash_prefix=None,
                progress=True,
            )

    def setup(self, threshold=0.85):
        self.threshold = threshold
        try_to_import_pillow()
        try_to_import_torch()
        try_to_import_torchvision()

        import torch
        import torch.nn.functional as F

        model_url = (
            "https://www.dropbox.com/s/85b63eahka5r439/emotion_detector.t7?raw=1"
        )
        model_weights_path = torch.hub.get_dir() + "/emotion_detector.t7"
        # pull model weights from dropbox if not present
        self._download_weights(model_url, model_weights_path)

        # helper class for VGG
        class VGG(torch.nn.Module):
            def __init__(self, vgg_name):
                super(VGG, self).__init__()
                self.features = self._make_layers(cfg[vgg_name])
                self.classifier = torch.nn.Linear(512, 7)

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
                        layers += [torch.nn.MaxPool2d(kernel_size=2, stride=2)]
                    else:
                        layers += [
                            torch.nn.Conv2d(in_channels, x, kernel_size=3, padding=1),
                            torch.nn.BatchNorm2d(x),
                            torch.nn.ReLU(inplace=True),
                        ]
                        in_channels = x
                layers += [torch.nn.AvgPool2d(kernel_size=1, stride=1)]
                return torch.nn.Sequential(*layers)

        # load model
        self.model = VGG("VGG19")

        # self.get_device() infers device from the loaded model, so not using it
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_state = torch.load(model_weights_path, map_location=device)
        self.model.load_state_dict(model_state["net"])
        self.model.eval()

        # for augmentation
        self.cut_size = 44

    def transforms_ed(self, frame):
        """
        Performs augmentation on input frame
        Arguments:
            frame (Tensor): Frame on which augmentation needs
            to be performed
        Returns:
            frame (Tensor): Augmented frame
        """
        from torchvision import transforms

        # convert to grayscale, resize and make tensor
        frame = frame.convert("L")
        frame = transforms.functional.resize(frame, (48, 48))
        frame = transforms.functional.to_tensor(frame)

        return frame

    def transform(self, images: np.ndarray):
        # reverse the channels from opencv
        from PIL import Image

        return self.transforms_ed(Image.fromarray(images[:, :, ::-1]))

    @property
    def labels(self) -> List[str]:
        return ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

    def forward(self, frames) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (Tensor): Frames on which predictions need
            to be performed
        Returns:
            outcome (pd.DataFrame): Emotion Predictions for input frames
        """

        # result dataframe
        outcome = []

        import torch
        import torch.nn.functional as F
        from torchvision import transforms

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
        outcome.append(
            {
                "labels": self.labels[predicted.item()],
                "scores": score.cpu().detach().numpy()[predicted.item()],
            }
        )

        return pd.DataFrame(outcome, columns=["labels", "scores"])

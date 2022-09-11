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
from typing import List

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
from skimage.transform import resize
from torch.autograd import Variable

from eva.configuration.dictionary import EVA_DEFAULT_DIR
from eva.udfs.abstract_udf import AbstractClassifierUDF
from eva.udfs.gpu_compatible import GPUCompatible

# VGG configuration
cfg = {
    "VGG11": [64, "M", 128, "M", 256, 256, "M", 512, 512, "M", 512, 512, "M"],
    "VGG13": [64, 64, "M", 128, 128, "M", 256, 256, "M", 512, 512, "M", 512, 512, "M"],
    "VGG16": [
        64,
        64,
        "M",
        128,
        128,
        "M",
        256,
        256,
        256,
        "M",
        512,
        512,
        512,
        "M",
        512,
        512,
        512,
        "M",
    ],
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


class EmotionDetector(AbstractClassifierUDF, GPUCompatible):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "EmotionDetector"

    def __init__(self, threshold=0.85):
        super().__init__()
        self.threshold = threshold

        # load model
        self.model = VGG("VGG19")
        model_state = torch.load(
            os.path.join(EVA_DEFAULT_DIR, "data", "models", "emotion_detector.t7")
        )
        self.model.load_state_dict(model_state["net"])

        # move to GPU and set to evaluation mode
        self.to_device("0")
        self.model.eval()

        # define the transforms
        self.cut_size = 44
        self.transforms = transforms.Compose(
            [
                transforms.TenCrop(self.cut_size),
                transforms.Lambda(
                    lambda crops: torch.stack(
                        [transforms.ToTensor()(crop) for crop in crops]
                    )
                ),
            ]
        )

    def to_device(self, device: str):
        print(f"to device {device}")
        gpu = "cuda:{}".format(device)
        self.model = self.model.to(torch.device(gpu))
        return self

    @property
    def labels(self) -> List[str]:
        return ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

    def classify(self, frames: pd.DataFrame) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed
        Returns:
            outcome (pd.DataFrame): Emotion Predictions for input frames
        """

        # convert frames to ndarray
        frames_list = frames.transpose().values.tolist()[0]
        frames = np.asarray(frames_list)

        # result dataframe
        outcome = pd.DataFrame()
        for frame in frames:

            # preprocess
            frame = np.dot(frame[..., :3], [0.299, 0.587, 0.114])
            frame = resize(frame, (48, 48), mode="symmetric").astype(np.uint8)
            frame = frame[:, :, np.newaxis]
            frame = np.concatenate([frame, frame, frame], axis=2)
            frame = Image.fromarray(frame)

            # transform frame
            inputs = self.transforms(frame)

            # predict
            ncrops, c, h, w = np.shape(inputs)
            inputs = inputs.view(-1, c, h, w)
            inputs = inputs.cuda()
            inputs = Variable(inputs)
            outputs = self.model(inputs)

            # avg over crops
            outputs_avg = outputs.view(ncrops, -1).mean(0)

            # get max index
            score = F.softmax(outputs_avg, dim=0)
            _, predicted = torch.max(outputs_avg.data, 0)

            # save results
            outcome = outcome.append(
                {
                    "labels": self.labels[predicted.item()],
                    "scores": score.cpu().detach().numpy()[predicted.item()],
                },
                ignore_index=True,
            )

        return outcome

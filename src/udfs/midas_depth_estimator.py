# coding=utf-8
# Copyright 2018-2020 EVA
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

import numpy as np
import pandas as pd
import torch
from torch import Tensor
from torchvision.transforms import Compose

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.udfs.pytorch_abstract_udf import PytorchAbstractUDF


class MidasDepthEstimator(PytorchAbstractUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "midas_depth_estimator"

    def __init__(self, threshold=0.85):
        super().__init__()
        self.model_type = "MiDaS_small" # "DPT_Large", "DPT_Hybrid"
        self.model = torch.hub.load("intel-isl/MiDaS", self.model_type)
        self.model.eval()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def transforms(self) -> Compose:
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        transform = midas_transforms.small_transform

        return transform

    def transform(self, images: np.ndarray):
        print(f"[Ani] Inside overriden transform")
        return self.transforms(images)

    @property
    def labels(self) -> List[str]:
        return [
            '__background__', 'person', 'bicycle', 'car', 'motorcycle',
            'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A',
            'stop sign',
            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
            'cow',
            'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack',
            'umbrella', 'N/A', 'N/A',
            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
            'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard',
            'surfboard', 'tennis racket',
            'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
            'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
            'hot dog', 'pizza',
            'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A',
            'dining table',
            'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote',
            'keyboard', 'cell phone',
            'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A',
            'book',
            'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]

    def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed

        Returns:
            tuple containing predicted_classes (List[List[str]]),
            predicted_boxes (List[List[BoundingBox]]),
            predicted_scores (List[List[float]])

        """
        print("[Ani] in function _get_predictions of MidasDepthEstimator")
        print(f"[Ani] frames shape: {frames.shape}")

        prediction = self.model(frames)
        print("[Ani] forward pass done")
        print(f"[Ani] prediction shape before interpolate {prediction.shape}")
        print(f'[Ani] frames.shape[:2]: {frames.shape[:2]}')

        # TODO: There seems to be a problem if I enter a bigger size. Need to see why. 
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=(90, 160),
            mode="bicubic",
            align_corners=False,
        ).squeeze()

        print("[Ani] end predictions")
        print(f"[Ani] prediction shape {prediction.shape}")

        outcome = pd.DataFrame()
        output_frames = prediction.detach().cpu().numpy()

        print(f"[Ani] output_frames shape {output_frames.shape}")
        print("[Ani] cumulate results")

        outcome = outcome.append(
            {
                'frames' : output_frames
            }, 
            ignore_index=True
        )

        print(f"[Ani] outcome shape: {outcome.shape}")

        return outcome

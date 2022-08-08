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
import numpy as np

import torch

from torch import Tensor
from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.pytorch_abstract_udf import PytorchAbstractUDF

import torchvision.transforms as T

from dlib import get_frontal_face_detector

class FaceDetector(PytorchAbstractUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "FaceDetector"

    def __init__(self, threshold=0.85):
        super().__init__()
        self.threshold = threshold

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return [
            "face"
        ]

    def rect_to_bb(self, rect):
        x = rect.left()
        y = rect.top()
        w = rect.right() - x 
        h = rect.bottom() - y 
        return (x, y, w, h)

    def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed
        Returns:
            face boxes (List[List[BoundingBox]])
        """
        detector = get_frontal_face_detector()

        copy = torch.squeeze(frames)
        transform = T.ToPILImage()
        copy2 = transform(copy)
        copy3 = np.array(copy2)
        detections, scores, _ = detector(copy3, 1, -1)

        bboxes = []
        for i, d in enumerate(detections):
            if scores[i] > self.threshold:
                bbox = rect_to_bb(d)
                bboxes.append(bbox)

        outcome = pd.DataFrame()
        outcome = outcome.append(
            {
                "bboxes": bboxes,
            },
            ignore_index=True)

        return outcome
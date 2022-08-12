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
import torchvision.transforms as T
from facenet_pytorch import MTCNN
from torch import Tensor

from eva.udfs.pytorch_abstract_udf import PytorchAbstractClassifierUDF


class FaceDetector(PytorchAbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    def __init__(self, threshold=0.85):
        super().__init__()
        self.threshold = threshold
        self.model = MTCNN()
        self.model.eval()

    @property
    def labels(self) -> List[str]:
        return []

    def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed
        Returns:
            face boxes (List[List[BoundingBox]])
        """

        copy = torch.squeeze(frames)
        transform = T.ToPILImage()
        pil_image = transform(copy)

        bboxes, scores = self.model.detect(img=pil_image)

        outcome = pd.DataFrame()
        outcome = outcome.append(
            {"bboxes": bboxes, "scores": scores}, ignore_index=True
        )

        return outcome

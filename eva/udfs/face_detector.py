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

import numpy as np
import pandas as pd
import torch
from facenet_pytorch import MTCNN

from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF
from eva.udfs.gpu_compatible import GPUCompatible
from eva.utils.logging_manager import logger


class FaceDetector(AbstractClassifierUDF, GPUCompatible):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    def setup(self, threshold=0.85):
        self.threshold = threshold
        self.model = MTCNN()

    @property
    def name(self) -> str:
        return "FaceDetector"

    def to_device(self, device: str):
        gpu = "cuda:{}".format(device)
        self.model = MTCNN(device=torch.device(gpu))
        return self

    @property
    def labels(self) -> List[str]:
        return []

    def forward(self, frames: pd.DataFrame) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed
        Returns:
            face boxes (List[List[BoundingBox]])
        """

        frames_list = frames.transpose().values.tolist()[0]
        frames = np.asarray(frames_list)
        detections = self.model.detect(frames)
        boxes, scores = detections
        outcome = pd.DataFrame()
        for frame_boxes, frame_scores in zip(boxes, scores):
            pred_boxes = []
            pred_scores = []
            if frame_boxes is not None and frame_scores is not None:
                if not np.isnan(pred_boxes):
                    pred_boxes = np.asarray(frame_boxes, dtype="int")
                    pred_scores = frame_scores
                else:
                    logger.warn(f"Nan entry in box {frame_boxes}")
            outcome = outcome.append(
                {"bboxes": pred_boxes, "scores": pred_scores},
                ignore_index=True,
            )

        return outcome

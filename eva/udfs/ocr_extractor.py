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

import easyocr
import numpy as np
import pandas as pd

from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF
from eva.udfs.gpu_compatible import GPUCompatible


class OCRExtractor(AbstractClassifierUDF, GPUCompatible):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    def to_device(self, device: str):
        """
        :param device:
        :return:
        """
        self.model = easyocr.Reader(["en"], gpu="cuda:{}".format(device), verbose=False)
        return self

    def setup(self, threshold=0.85):
        self.threshold = threshold
        self.model = easyocr.Reader(["en"], verbose=False)

    @property
    def name(self) -> str:
        return "OCRExtractor"

    @property
    def labels(self) -> List[str]:
        """
        Empty as there are no labels required for
        optical character recognition
        """
        return

    def forward(self, frames: np.ndarray) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (tensor): Frames on which OCR needs
            to be performed
        Returns:
            tuple containing OCR labels (List[List[str]]),
            predicted_boxes (List[List[BoundingBox]]),
            predicted_scores (List[List[float]])
        """

        frames_list = frames.values.tolist()
        frames = np.array(frames_list)

        # Get detections
        detections_in_frames = self.model.readtext_batched(np.vstack(frames))

        outcome = []

        for i in range(0, frames.shape[0]):
            labels = []
            bboxes = []
            scores = []
            for detection in detections_in_frames[i]:
                labels.append(detection[1])
                bboxes.append(detection[0])
                scores.append(detection[2])

            outcome.append(
                {
                    "labels": list(labels),
                    "bboxes": list(bboxes),
                    "scores": list(scores),
                }
            )

        return pd.DataFrame(outcome, columns=["labels", "bboxes", "scores"])

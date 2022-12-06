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
import PIL
import pytesseract
from detoxify import Detoxify

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF
from eva.utils.logging_manager import logger


class HarmfulMemeDetector(AbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "HarmfulMemeDetector"

    def setup(self, threshold=0.2):
        logger.warn("setup start")
        self.threshold = threshold
        self.model = Detoxify("original")
        logger.warn("setup finish")

    @property
    def input_format(self) -> FrameInfo:
        logger.warn("input_format start")
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        logger.warn("labels start")
        return ["toxic", "not toxic"]

    def forward(self, frames: np.ndarray) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed
        Returns:
            outcome (List[Str])
        """
        # reconstruct dimension of the input
        frames_list = frames.values.tolist()
        frames = np.array(frames_list)
        frames = np.squeeze(frames, 1)
        logger.warn(frames.shape)
        # frames = frames[0][0]

        outcome = pd.DataFrame()

        for i in range(0, frames.shape[0]):
            frame = frames[i]

            image = PIL.Image.fromarray(frame.astype("uint8"), "RGB")
            text = pytesseract.image_to_string(image)
            logger.warn(text)
            prediction_result = self.model.predict(text)
            if prediction_result["toxicity"] >= self.threshold:
                outcome = outcome.append({"labels": "toxic"}, ignore_index=True)
            else:
                outcome = outcome.append({"labels": "not toxic"}, ignore_index=True)
        return outcome

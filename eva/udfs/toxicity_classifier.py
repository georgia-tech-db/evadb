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

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF
from eva.utils.logging_manager import logger

try:
    import detoxify
except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install detoxify`"
    )

class ToxicityClassifier(AbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "ToxicityClassifier"

    def setup(self, threshold=0.2):
        self.threshold = threshold
        self.model = detoxify.Detoxify("original")

    @property
    def input_format(self) -> str:
        return str

    @property
    def labels(self) -> List[str]:
        return ["toxic", "not toxic"]

    def forward(self, text: pd.DataFrame) -> pd.DataFrame:
        """
        Performs predictions on input text
        Arguments:
            text (pd.DataFrame): Dataframe with sentences on which predictions need to be performed
        Returns:
            outcome (List[Str])
        """
        # reconstruct dimension of the input
        outcome = pd.DataFrame()

        for i in range(0, text.shape[0]):
            text = text[i]
            logger.warn(text)
            prediction_result = self.model.predict(text)
            if prediction_result["toxicity"] >= self.threshold:
                outcome = outcome.append({"labels": "toxic"}, ignore_index=True)
            else:
                outcome = outcome.append({"labels": "not toxic"}, ignore_index=True)

        return outcome
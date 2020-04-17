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
from abc import ABCMeta, abstractmethod
from typing import List

import numpy as np
import pandas as pd

from src.models.catalog.frame_info import FrameInfo


class AbstractClassifierUDF(metaclass=ABCMeta):
    """
    Abstract class for UDFs. All the UDFs which perform classification
    inherit this calls.

    Load and initialize the machine learning model in the __init__.

    """

    def __init__(self):
        pass

    @property
    @abstractmethod
    def input_format(self) -> FrameInfo:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def labels(self) -> List[str]:
        """
        Returns:
            List[str]: list of labels the classifier predicts
        """

    @abstractmethod
    def classify(self, frames: np.ndarray) -> List[pd.DataFrame]:
        """
        Takes as input a batch of frames and returns the predictions by
        applying the classification model.

        Arguments:
            frames (np.ndarray): Input batch of frames on which prediction
            needs to be made

        Returns:
            List[DataFrame]: The predictions made by the classifier
        """

    def __call__(self, *args, **kwargs):
        self.classify(*args, **kwargs)

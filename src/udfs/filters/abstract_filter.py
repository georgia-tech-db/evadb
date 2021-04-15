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

import numpy as np
import pandas as pd

from src.models.catalog.frame_info import FrameInfo


class AbstractFilter(metaclass=ABCMeta):
    """
    Abstract class for filter UDFs. All the filter UDFs inherit this class.

    Load and initialize any necessary parameters in the __init__.
    """

    def __init__(self):
        pass

    @property
    @abstractmethod
    def input_format(self) -> FrameInfo:
        # TODO: do we need this?
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def classify(self, frames: np.ndarray) -> pd.DataFrame:
        """
        Takes as input a batch of frames and returns true or false
        predictions by applying the filter.

        Arguments:
            frames (np.ndarray): Input batch of frames on which prediction
            needs to be made

        Returns:
            DataFrame: The predictions made by the filter
        """

    def __call__(self, *args, **kwargs):
        return self.classify(*args, **kwargs)

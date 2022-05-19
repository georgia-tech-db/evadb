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
from abc import ABCMeta, abstractmethod

import numpy as np

from eva.models.catalog.frame_info import FrameInfo


class AbstractEffectUDF(metaclass=ABCMeta):
    """
    Abstract class for UDFs. All the UDFs which apply filters
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

    @abstractmethod
    def apply(self, frames: np.ndarray) -> np.ndarray:
        """
        Takes as input a batch of frames and returns the frames with the 
        filter applied to them.

        Arguments:
            frames (np.ndarray): Input batch of frames on which to apply filter
        
        Returns:
            np.ndarray: The same frames with the filter applied
        """

    def __call__(self, *args, **kwargs):
        return self.apply(*args, **kwargs)


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
from typing import List, Union

import pandas as pd
from numpy.typing import ArrayLike

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace

InputType = Union[pd.DataFrame, ArrayLike]


class AbstractUDF(metaclass=ABCMeta):
    """
    Abstract class for UDFs. All the UDFs in EVA will inherit from this.

    Load and initialize the machine learning model in the __init__.

    """

    def __init__(self, *args, **kwargs):
        self.setup(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.forward(args[0])

    def __str__(self):
        return self.name

    """Abstract Methods all UDFs must implement. """

    @abstractmethod
    def setup(self, *args, **kwargs) -> None:
        """
        Do necessary setup in here. Gets called automatically on intialization.
        """
        pass

    @abstractmethod
    def forward(self, frames: InputType) -> InputType:
        """
        Implement UDF function call by overriding this function.
        Gets called automatically by __call__.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)


class AbstractClassifierUDF(AbstractUDF):
    @property
    @abstractmethod
    def labels(self) -> List[str]:
        """
        Returns:
            List[str]: list of labels the classifier predicts
        """
        pass


class AbstractTransformationUDF(AbstractUDF):
    @abstractmethod
    def transform(self, frames: ArrayLike) -> ArrayLike:
        """
        Takes as input a batch of frames and transforms them
        by applying the frame transformation model.

        Arguments:
            frames: Input batch of frames on which prediction
            needs to be made

        Returns:
            Transformed frames
        """

    def __call__(self, *args, **kwargs):
        return self.transform(*args, **kwargs)

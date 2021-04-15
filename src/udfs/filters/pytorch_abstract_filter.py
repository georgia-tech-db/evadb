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

import pandas as pd
from torch import nn

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.udfs.filters.abstract_filter import AbstractFilter
from src.udfs.gpu_compatible import GPUCompatible


class PytorchAbstractFilter(AbstractFilter, nn.Module, GPUCompatible):
    """
    A PyTorch based filter.
    """

    def __init__(self):
        AbstractFilter.__init__(self)
        nn.Module.__init__(self)

    def get_device(self):
        return next(self.parameters()).device

    @property
    def name(self) -> str:
        return "object_filter"

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    def classify(self, frames: pd.DataFrame) -> pd.DataFrame:
        pass

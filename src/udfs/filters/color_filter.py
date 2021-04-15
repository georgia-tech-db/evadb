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

import numpy as np
import pandas as pd

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.udfs.filters.abstract_filter import AbstractFilter


class ColorFilter(AbstractFilter):
    """
    Filter for removing frames based on presence or absence of colored objects.
    """

    def __init__(self):
        AbstractFilter.__init__(self)
        # TODO: don't hardcode this
        self.threshold = 161933.5

    @property
    def name(self) -> str:
        return "color_filter"

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    def classify(self, frames: pd.DataFrame) -> pd.DataFrame:
        # TODO: is there a better way to do this?
        frames = np.stack(frames.to_numpy()[:, 0])
        redness = np.sum(np.clip(
            frames[:, :, :, 0] - frames[:, :, :, 1] /
            2 - frames[:, :, :, 2] / 2,
            0, None), axis=(1, 2))
        return pd.DataFrame(redness > self.threshold)

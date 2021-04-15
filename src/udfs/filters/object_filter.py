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


class ObjectFilter(AbstractFilter):
    """
    Filter for removing frames based on presence or absence of objects.
    """

    def __init__(self):
        AbstractFilter.__init__(self)
        # TODO: don't hardcode this
        self.avg_frame = np.load("src/udfs/filters/m30.npy")
        self.threshold = 1464.2065

    @property
    def name(self) -> str:
        return "object_filter"

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    def classify(self, frames: pd.DataFrame) -> pd.DataFrame:
        # TODO: is there a better way to do this?
        frames = np.stack(frames.to_numpy()[:, 0])
        distances = np.sqrt(
            np.sum((frames - self.avg_frame) ** 2, axis=(1, 2, 3)))
        return pd.DataFrame(distances > self.threshold)

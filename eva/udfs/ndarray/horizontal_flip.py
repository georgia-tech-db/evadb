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
import cv2
import numpy as np
import pandas as pd

from eva.udfs.abstract.abstract_udf import AbstractUDF

class HorizontalFlip(AbstractUDF):
    def setup(self):
        pass

    @property
    def name(self):
        return "HorizontalFlip"

    def forward(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        Apply horizontal flip to the frame

         Returns:
             ret (pd.DataFrame): The modified frame.
        """

        def horizontalFlip(row: pd.Series) -> np.ndarray:
            row = row.to_list()
            frame = row[0]

            frame = cv2.flip(frame, 1)

            return frame

        ret = pd.DataFrame()
        ret["horizontally_flipped_frame_array"] = frame.apply(horizontalFlip, axis=1)
        return ret

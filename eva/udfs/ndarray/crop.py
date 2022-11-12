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
import numpy as np
import pandas as pd

from eva.udfs.abstract.abstract_udf import AbstractUDF


class Crop(AbstractUDF):
    def setup(self):
        pass

    @property
    def name(self):
        return "Crop"

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crop the frame given the bbox - Crop(frame, bbox)
        If one of the side of the crop box is 0, it automatically sets it to 1 pixel

        Returns:
            ret (pd.DataFrame): The cropped frame.
        """

        def crop(row: pd.Series) -> np.ndarray:
            row = row.to_list()
            frame = row[0]
            bboxes = row[1]

            x0, y0, x1, y1 = np.asarray(bboxes, dtype="int")
            # make sure the bbox is valid
            x0 = max(0, x0)
            y0 = max(0, y0)

            if x1 == x0:
                x1 = x0 + 1

            if y1 == y0:
                y1 = y0 + 1

            return frame[y0:y1, x0:x1]

        ret = pd.DataFrame()
        ret["cropped_frame_array"] = df.apply(crop, axis=1)
        return ret

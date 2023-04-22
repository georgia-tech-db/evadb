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

class ToGrayscale(AbstractUDF):
    def setup(self):
        pass

    @property
    def name(self):
        return "ToGrayscale"

    def forward(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the frame from BGR to grayscale

         Returns:
             ret (pd.DataFrame): The modified frame.
        """

        def toGrayscale(row: pd.Series) -> np.ndarray:
            row = row.to_list()
            frame = row[0]

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            return frame

        ret = pd.DataFrame()
        ret["grayscale_frame_array"] = frame.apply(toGrayscale, axis=1)
        return ret

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

color = (207, 248, 64)
thickness = 4


class FrameId(AbstractUDF):
    def setup(self):
        pass

    @property
    def name(self):
        return "FrameId"

    def forward(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        Put the frame id at the bottom left of each frame

         Returns:
             ret (pd.DataFrame): The modified frame.
        """

        def frameId(row: pd.Series) -> np.ndarray:
            row = row.to_list()
            frame = row[0]
            frame_id = row[1]

            frame = cv2.putText(
                frame,
                str(frame_id),
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                thickness,
            )
            # since cv2 by default reads an image in BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            return frame

        ret = pd.DataFrame()
        ret["frame_array_with_id"] = frame.apply(frameId, axis=1)
        return ret

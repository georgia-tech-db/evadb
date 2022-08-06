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
import pandas as pd
import numpy as np

from eva.udfs.ndarray_udfs.abstract_ndarray_udfs import AbstractNdarrayUDF


class Crop(AbstractNdarrayUDF):

    def name(self):
        return 'Crop'

    def exec(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crop the frame given the bbox.
        Crop(frame, bbox)
        """
        def crop(row: pd.Series) -> np.ndarray:
            frame = row['data']
            h, w, _ = frame.shape
            #bboxes = list(map(int, map(float, row['bboxes'][1:-1].split(','))))
            x0, y0, x1, y1 = bboxes
            if y0 > y1:
                y0, y1 = y1, y0
            if x0 > x1:
                x0, x1 = x1, x0

            if y0 == y1:
                if y1 + 1 < h:
                    y1 = y1 + 1
                else:
                    y0 = y0 - 1
            if x0 == x1:
                if x1 + 1 < w:
                    x1 = x1 + 1
                else:
                    x0 = x0 - 1

            return frame[y0:y1, x0:x1]

        ret = pd.DataFrame()
        ret['data'] = df.apply(crop, axis=1)

        return ret

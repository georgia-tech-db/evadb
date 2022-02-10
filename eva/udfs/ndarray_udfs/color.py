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
import numpy as np
from eva.udfs.ndarray_udfs.abstract_ndarray_udfs import AbstractNdarrayUDF

class Color(AbstractNdarrayUDF):
    def name(self):
        return 'COLOR'

    def exec(self, inp: pd.DataFrame) -> pd.DataFrame:
        result = []
        for _, row in inp.iterrows():
            data = row['data']
            boxes = row['boxes']
            x1, y1 = boxes[0]
            x2, y2 = boxes[1]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            object = data[x1 : x2, y1 : y2 ]
            color_vals = np.mean(object, axis=(0, 1))
            colors = ['RED', 'GREEN', 'BLUE']
            max_color_index = color_vals.argmax()
            result.append(colors[max_color_index])

        return pd.DataFrame({'color': result})
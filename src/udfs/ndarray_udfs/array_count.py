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
from src.udfs.ndarray_udfs.abstract_ndarray_udfs import AbstractNdarrayUDF


class Array_Count(AbstractNdarrayUDF):

    @property
    def name(self) -> str:
        return 'Array_Count'

    def exec(self, inp: pd.DataFrame, **kwargs):
        # print("input:", inp)
        # print("name:", kwargs.get("name"))

        # input should just be a single column (Data Series or DF with one column)

        # iterate over rows and see if match with search element

        # inp:   col
        #   0: [["A"], ["A"], ["B"]] size: (0,3)
        #   1: [["A"], ["B"], ["B"]] label: ["A"]
        # return: [[0, 2],
        #          [1, 1]]

        name = kwargs.get("name")

        count = 0
        if name:
            df = inp[inp['label'].astype(str).str.contains(name)]
            count = df.shape[0]

        return pd.DataFrame([{'count': count}])

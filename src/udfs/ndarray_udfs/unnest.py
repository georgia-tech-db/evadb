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
from itertools import zip_longest

from src.udfs.ndarray_udfs.abstract_ndarray_udfs import AbstractNdarrayUDF


class Unnest(AbstractNdarrayUDF):
    def name(self):
        return 'UNNEST'

    def xplode(self, df, explode, zipped=True):
        # https://stackoverflow.com/questions/53218931/how-to-unnest-explode-a-column-in-a-pandas-dataframe   # noqa
        rest = {*df} - {*explode}
        zipped = zip(zip(*map(df.get, rest)), zip(*map(df.get, explode)))
        tups = [tup + exploded
                for tup, pre in zipped
                for exploded in zip_longest(*pre)]

        return pd.DataFrame(tups, columns=[*rest, *explode])[[*df]]

    def exec(self, inp: pd.DataFrame) -> pd.DataFrame:
        """
        1. infer using the first row, design a better way without compromising
        speed
        2. Append dummy column to keep track of original index
        """
        first_row = inp.iloc[0]
        explode = []
        dummy_idx = 'dummy_idx'
        for col in inp.columns:
            if isinstance(first_row[col], np.ndarray):
                explode.append(col)
        inp[dummy_idx] = inp.index
        res = self.xplode(inp, explode)
        res = res.set_index(dummy_idx)
        res.index.name = None
        return res

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


class Array_Count(AbstractUDF):
    @property
    def name(self) -> str:
        return "Array_Count"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        """
        It will return a count of search element for each tuple.
        The idea is to flatten the input array along the first dimension and
        count the search element in this flattened array.
        For example,
        a tuple of shape (3,4,5) will be flattened into three (4,5) elements.
        And the search key is expected to be of shape (4,5),
        else we throw an error.

        inp: DataFrame
            col1        col2
        0   ndarray1    search_key
        1   ndarray2    search_key

        out: DataFrame
            count
        0   int
        1   int

        """
        # sanity check
        if len(inp.columns) != 2:
            raise ValueError("input contains more than one column")

        search_element = inp[inp.columns[-1]][0]
        values = pd.DataFrame(inp[inp.columns[0]])

        count_result = values.apply(
            lambda x: self.count_in_row(x[0], search_element), axis=1
        )

        return pd.DataFrame({"key_count": count_result.values})

    def count_in_row(self, row_val, search_element):
        # change the row and search element to numpy array
        row_val = np.array(row_val)
        search_element = np.array(search_element)

        # checks if dimension diff is one between
        # row_val and search_element
        if row_val.ndim - search_element.ndim != 1:
            raise ValueError("inconsistent dimensions for row value and search element")

        result = row_val == search_element
        # reshape along the first dimension and then
        # check how many time search element exists
        return result.reshape(result.shape[0], -1).all(axis=1).sum()

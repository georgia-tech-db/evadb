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
from src.udfs.ndarray_udfs.abstract_ndarray_udfs import AbstractNdarrayUDF


class Array_Count(AbstractNdarrayUDF):

    @property
    def name(self) -> str:
        return 'Array_Count'

    def exec(self, inp: pd.DataFrame):
        # input should just be a single column
        # (Data Series or DF with one column)

        # pre conditions: #####################################################
        # check if numpy array, else throw
        # check number of dimensions of numpy array
        # check number of dimensions of searchElement if array
        # if number of dimensions of searchElement not less by 1 than numpy
        # array throw

        # loop over and apply count function
        # convert to pd data frame and then add index as a column (optional)

        # inp (1 column), label: ["A"]
        # row 0: [["A"], ["A"], ["B"]]
        # row 1: [["A"], ["B"], ["B"]]
        # return: [2,
        #          1]
        # ##########################################################################

        # sanity check
        if len(inp.columns) != 2:
            raise ValueError('input contains more than one column')

        search_element = inp[inp.columns[-1]][0]
        values = pd.DataFrame(inp[inp.columns[0]])

        count_result = values.apply(
            lambda x: self.count_in_row(
                x[0], search_element), axis=1)

        return pd.DataFrame({'count': count_result.values})
        # return pd.DataFrame({'id': count_result.index, 'count':
        # count_result.values})

    def count_in_row(self, row_val, search_element):
        # checks that if search_element is a string or int, then row array
        # should be one dimension
        if isinstance(row_val, list) and isinstance(
                search_element, (str, int)):
            if np.array(row_val).ndim > 1:
                raise ValueError(
                    'inconsistent dimensions for row value and search element')
            return row_val.count(search_element)

        # if row_val is a np.ndarray then search_element should be one too
        if isinstance(row_val, np.ndarray) and isinstance(
                search_element, (str, int)):
            raise ValueError(
                'inconsistent dimensions for row value and search element')

        # checks that if row_val and search_element are numpy arrays then
        # dimension diff is one
        if isinstance(row_val, np.ndarray) and isinstance(
                search_element, (np.ndarray, list)):
            nd_search_element = search_element
            # if search_element is a list convert to ndarray
            if isinstance(nd_search_element, list):
                nd_search_element = np.array(nd_search_element)
            if row_val.ndim - nd_search_element.ndim != 1:
                raise ValueError(
                    'inconsistent dimensions for row value and search element')
            # vectorized approach for searching elements
            return np.sum(row_val == nd_search_element.all(1))

        raise ValueError('failed to recognize dimensions')

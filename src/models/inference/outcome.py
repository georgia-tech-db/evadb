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


class Outcome:
    """
    Data model used to store the outcome of each function.

    Arguments:
        data (pd.DataFrame): actual pandas dataframe containing the information
        identifier (str): the identifier string for the outcomes.
        Default comparisons will be performed on this field.
    """

    def __init__(self, data: pd.DataFrame, identifier: str):
        self._data = data
        self._identifier = identifier

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    def __getattr__(self, item):
        if item in self._data.columns:
            return Outcome(self._data[[item]], item)

    def __eq__(self, other):
        if isinstance(other, Outcome):
            return self._identifier == other._identifier and \
                self._data.equals(other._data)

        return len(self._data[self._data[self._identifier] == other]) > 0

    def __le__(self, other):
        return len(self._data[self._data[self._identifier] <= other]) > 0

    def __ge__(self, other):
        return len(self._data[self._data[self._identifier] >= other]) > 0

    def __gt__(self, other):
        return len(self._data[self._data[self._identifier] > other]) > 0

    def __lt__(self, other):
        return len(self._data[self._data[self._identifier] < other]) > 0

    def __ne__(self, other):
        return len(self._data[self._data[self._identifier] == other]) == 0

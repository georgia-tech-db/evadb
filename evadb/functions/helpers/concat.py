# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from evadb.functions.abstract.abstract_function import AbstractFunction


class Concat(AbstractFunction):
    def setup(self):
        pass

    @property
    def name(self):
        return "CONCAT"

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Concats all the df values into one.

        Returns:
            ret (pd.DataFrame): Concatenated string.
        """

        ret = pd.DataFrame()
        ret["output"] = pd.Series(df.fillna("").values.tolist()).str.join("")
        return ret

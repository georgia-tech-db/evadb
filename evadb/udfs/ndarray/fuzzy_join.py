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
from thefuzz import fuzz

from evadb.udfs.abstract.abstract_udf import AbstractUDF


class FuzzDistance(AbstractUDF):
    def setup(self):
        pass

    @property
    def name(self):
        return "FuzzDistance"

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Find the distance between two dataframes using <> distance metric.

        Returns:
            ret (pd.DataFrame): The cropped frame.
        """
        ret = pd.DataFrame()
        ret["distance"] = df.apply(
            lambda row: fuzz.ratio(str(row[0]), str(row[1])), axis=1
        )
        return ret

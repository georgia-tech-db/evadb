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

from thefuzz import fuzz
from thefuzz import process

from eva.udfs.abstract.abstract_udf import AbstractUDF

from test.util import create_sample_image, load_inbuilt_udfs


class FuzzyJoin(AbstractUDF):
    def setup(self):
        pass

    @property
    def name(self):
        return "FuzzyJoin"

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Find the distance between two dataframes using <> distance metric. 

        Returns:
            ret (pd.DataFrame): The cropped frame.
        """

        def fuzzyjoin(row: pd.Series) -> float:
            
            print("row")
            print(type(row))
            print(row.shape )
            ratio = fuzz.ratio(row[0], row[1])
            print(ratio)

            return 0.1

            #create duplicate column to retain team name from df2
            df2['team_match'] = df2['team']

            #convert team name in df2 to team name it most closely matches in df1
            df2['team'] = df2['team'].apply(lambda x: difflib.get_close_matches(x, df1['team'])[0])

            #merge the DataFrames into one
            df3 = df1.merge(df2)

        ret = pd.DataFrame()
        ret["distance"] = df.apply(fuzzyjoin, axis=1)
        return ret

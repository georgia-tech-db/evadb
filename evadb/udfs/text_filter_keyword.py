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
import numpy as np
import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe


class TextFilterKeyword(AbstractUDF):
    @setup(cacheable=False, udf_type="TextProcessing", batchable=False)
    def setup(self):
        pass

    @property
    def name(self) -> str:
        return "TextFilterKeyword"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data", "keyword"],
                column_types=[NdArrayType.STR, NdArrayType.STR],
                column_shapes=[(1), (1)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["filtered"],
                column_types=[NdArrayType.STR],
                column_shapes=[(1)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        def _forward(row: pd.Series) -> np.ndarray:
            import re

            data = row.iloc[0]
            keywords = row.iloc[1]
            flag = False
            for i in keywords:
                pattern = rf"^(.*?({i})[^$]*)$"
                match_check = re.search(pattern, data, re.IGNORECASE)
                if match_check:
                    flag = True
            if flag is False:
                return data
            flag = False

        ret = pd.DataFrame()
        ret["filtered"] = df.apply(_forward, axis=1)
        return ret

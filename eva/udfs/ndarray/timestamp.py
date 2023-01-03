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
import time

import pandas as pd

from eva.udfs.abstract.abstract_udf import AbstractUDF


class Timestamp(AbstractUDF):
    @property
    def name(self) -> str:
        return "Timestamp"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        """
        inp: DataFrame -> out: DataFrame
            second           timestamp
        0   int           0   string
        1   int           1   string
        """

        # Sanity check
        if len(inp.columns) != 1:
            raise ValueError("input must only contain one column (seconds)")

        seconds = pd.DataFrame(inp[inp.columns[0]])
        timestamp_result = seconds.apply(lambda x: self.format_timestamp(x[0]), axis=1)
        outcome = pd.DataFrame({"timestamp": timestamp_result.values})
        return outcome

    def format_timestamp(self, num_of_seconds):
        timestamp = time.strftime("%H:%M:%S", time.gmtime(num_of_seconds))
        return timestamp

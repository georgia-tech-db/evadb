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
import cv2
import numpy as np
import pandas as pd

from eva.executor.executor_utils import ExecutorError
from eva.udfs.abstract.abstract_udf import AbstractUDF


class Open(AbstractUDF):
    def setup(self):
        # cache data to avoid expensive open files on disk
        self._data_cache = dict()

    @property
    def name(self):
        return "Open"

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Open image from server-side path.

        Returns:
            (pd.DataFrame): The opened image.
        """

        def _open(row: pd.Series) -> np.ndarray:
            path_str = row[0]
            if path_str in self._data_cache:
                data = self._data_cache[path_str]
            else:
                try:
                    data = cv2.imread(path_str)
                except Exception as e:
                    raise ExecutorError(str(e))

            self._data_cache[path_str] = data

            return data

        ret = pd.DataFrame()
        ret["data"] = df.apply(_open, axis=1)
        return ret

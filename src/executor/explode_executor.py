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
from typing import Iterator

from src.models.storage.batch import Batch
from src.executor.abstract_executor import AbstractExecutor
from src.planner.explode_plan import ExplodePlan
import pandas as pd
import numpy as np


class ExplodeExecutor(AbstractExecutor):
    """
    Executor for explode operator to explode nested list.

    Arguments:
        node (AbstractPlan): ExplodePlan

    """

    def __init__(self, node: ExplodePlan):
        super().__init__(node)
        self._column_list = node.column_list

    def validate(self):
        pass

    @staticmethod
    def is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def exec(self) -> Iterator[Batch]:
        for batch in self.children[0].exec():
            if not batch.empty():
                frames: pd.DataFrame = batch.frames
                nested_cols = {}
                flat_cols = {}
                len_arr = []

                col_names = [col.col_name for col in self._column_list]
                for col_name in col_names:
                    if col_name not in frames.columns:
                        raise KeyError("Column doesn't exist in "
                                       "the data frame: {}"
                                       .format(col_name))

                for col_name in frames.columns:
                    col = batch.column_as_numpy_array(col_name)
                    if len(col) == len(frames) and col.dtype != np.object:
                        flat_cols[col_name] = col
                    else:
                        flat_col = np.concatenate(col)
                        nested_cols[col_name] = flat_col
                        if len(len_arr) == 0:
                            len_arr = [len(r) for r in col]

                result_dict = {}
                for k, v in nested_cols.items():
                    result_dict[k] = v.tolist()
                for k, v in flat_cols.items():
                    result_dict[k] = np.repeat(v, len_arr).tolist()
                batch._frames = pd.DataFrame.from_dict(result_dict)

            yield batch

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
from src.planner.unnest_plan import UnnestPlan
from src.utils.logging_manager import LoggingManager, LoggingLevel
import pandas as pd
import numpy as np

class UnnestExecutor(AbstractExecutor):
    """
    Merge the seq scan queries
    Arguments:
        node (AbstractPlan): The UnionPlan

    """

    def __init__(self, node: UnnestPlan):
        super().__init__(node)
        self._column_list = node.column_list

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        for batch in self.children[0].exec():
            if not batch.empty():
                print(batch.frames)
                frames: pd.DataFrame = batch.frames
                print(frames.columns[0])

                first_row = frames.iloc[0]
                len_arr = []
                for column in self._column_list:
                    col_name = column.col_name
                    if col_name not in frames.columns:
                        raise KeyError("Column doesn't exist in the data frame: {}".format(column.col_name))
                    element = first_row[col_name]
                    if type(element) == list and len_arr == []:
                        col_list = frames[col_name].values.tolist()
                        len_arr = [len(r) for r in col_list]

                # Asserting all the lists in the same row
                # has the same length across the columns
                unnested_list = []
                for column in frames.columns:
                    if type(first_row[column]) == list:
                        unnested_list.append(np.concatenate(frames[column].values.tolist()))
                        print(len(unnested_list[-1]))
                    else:
                        unnested_list.append(np.repeat(frames[column], len_arr))
                        print(len(unnested_list[-1]))
                batch._frames = pd.DataFrame(np.column_stack(unnested_list), columns=frames.columns)

            yield batch

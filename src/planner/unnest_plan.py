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
from src.catalog.models.df_metadata import DataFrameMetadata
from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanNodeType
from src.parser.table_ref import TableRef
from src.catalog.models.df_column import DataFrameColumn
from typing import List

class UnnestPlan(AbstractPlan):
    """
    This is the plan used for retrieving the frames from the storage and
    and returning to the higher levels.

    Arguments:
        video (DataFrameMetadata): Required meta-data for fetching data
        batch_size (int): size of batch frame
        skip_frames (int): skip frequency
        offset (int): storage offset for retrieving data
        limit (int): limit on data records to be retrieved
        total_shards (int): number of shards of data (if sharded)
        curr_shard (int): current curr_shard if data is sharded
    """

    def __init__(self, column_list: List[DataFrameColumn]):
        super().__init__(PlanNodeType.UNNSET)
        self._column_list = column_list

    @property
    def column_list(self):
        return self._column_list

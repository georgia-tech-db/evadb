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
from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanOprType
from pathlib import Path
from src.catalog.models.df_metadata import DataFrameMetadata


class LoadDataPlan(AbstractPlan):
    """
    This plan is used for storing information required for load data
    operations.

    Arguments:
        table_metainfo(DataFrameMetadata): table metadata info to load into
        file_path(Path): file path from where we will load the data
        """

    def __init__(self, table_metainfo: DataFrameMetadata, file_path: Path):
        super().__init__(PlanOprType.LOAD_DATA)
        self._table_metainfo = table_metainfo
        self._file_path = file_path

    @property
    def table_metainfo(self):
        return self._table_metainfo

    @property
    def file_path(self):
        return self._file_path

    def __str__(self):
        print_str = 'LoadDataPlan(table_id={},file_path={})'.format(
            self.table_metainfo, self.file_path)
        return print_str

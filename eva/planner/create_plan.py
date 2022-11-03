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
from typing import List

from eva.catalog.models.df_column import DataFrameColumn
from eva.parser.table_ref import TableRef
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class CreatePlan(AbstractPlan):
    """
    This plan is used for storing information required for create table
    operations.
    Arguments:
        video_ref {TableRef} -- video ref for table to be created in storage
        column_list {List[DataFrameColumn]} -- Columns to be added
        if_not_exists {bool} -- Whether to override if there is existing table
    """

    def __init__(
        self,
        table_ref: TableRef,
        column_list: List[DataFrameColumn],
        if_not_exists: bool = False,
    ):
        super().__init__(PlanOprType.CREATE)
        self._table_ref = table_ref
        self._column_list = column_list
        self._if_not_exists = if_not_exists

    @property
    def table_ref(self):
        return self._table_ref

    @property
    def if_not_exists(self):
        return self._if_not_exists

    @property
    def column_list(self):
        return self._column_list

    def __str__(self):
        return "CreatePlan(table_ref={}, \
            column_list={}, \
            if_not_exists={})".format(
            self._table_ref, self._column_list, self._if_not_exists
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_ref,
                self.if_not_exists,
                tuple(self.column_list),
            )
        )

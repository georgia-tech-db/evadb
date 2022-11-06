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

from eva.parser.create_statement import ColumnDefinition
from eva.parser.table_ref import TableRef
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class CreateMaterializedViewPlan(AbstractPlan):
    """
    This plan is used for storing information required for creating
    materialized view.
    Arguments:
        view {TableRef} -- table ref for view to be created in storage
        col_list{List[ColumnDefinition]} -- column names in the view
        if_not_exists {bool} -- Whether to override if there is existing view
    """

    def __init__(
        self,
        view: TableRef,
        columns: List[ColumnDefinition],
        if_not_exists: bool = False,
    ):
        super().__init__(PlanOprType.CREATE_MATERIALIZED_VIEW)
        self._view = view
        self._columns = columns
        self._if_not_exists = if_not_exists

    @property
    def view(self):
        return self._view

    @property
    def if_not_exists(self):
        return self._if_not_exists

    @property
    def columns(self):
        return self._columns

    def __str__(self):
        return "CreateMaterializedViewPlan(view={}, \
            columns={}, \
            if_not_exists={})".format(
            self._view, self._columns, self._if_not_exists
        )

    def __hash__(self) -> int:
        return hash(
            (super().__hash__(), self.view, self.if_not_exists, tuple(self.columns))
        )

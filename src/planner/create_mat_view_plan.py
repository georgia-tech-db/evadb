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
from src.parser.table_ref import TableRef
from src.parser.select_statement import SelectStatement
from src.parser.create_statement import ColumnDefinition

from typing import List


class CreateMaterializedViewPlan(AbstractPlan):
    """
    This plan is used for storing information required for creating materialized view.
    Arguments:
        view {TableRef} -- table ref for view to be created in storage
        col_list{List[ColumnDefinition]} -- column names in the view
        query{SelectStatement} -- query used to populate the created view
        if_not_exists {bool} -- Whether to override if there is existing view
    """

    def __init__(self, view: TableRef,
                 col_list: List[ColumnDefinition],
                 query: SelectStatement,
                 if_not_exists: bool = False):
        super().__init__(PlanOprType.CREATE_MATERIALIZED_VIEW)
        self._view = view
        self._col_list = col_list
        self._if_not_exists = if_not_exists
        self._query = query

    @property
    def view(self):
        return self._view

    @property
    def if_not_exists(self):
        return self._if_not_exists

    @property
    def query(self):
        return self._query

    @property
    def col_list(self):
        return self._col_list

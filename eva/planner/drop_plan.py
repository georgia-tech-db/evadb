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
from typing import List

from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType
from eva.parser.table_ref import TableRef


class DropPlan(AbstractPlan):
    """
    This plan is used for storing information required for drop table
    operations.
    Arguments:
        table_ref {TableRef} -- table ref for table to be truncated in storage
        table_id {int} -- catalog table id for the table
    """

    def __init__(self, table_refs: List[TableRef],
                 if_exists: bool,
                 table_ids: List[int]):
        super().__init__(PlanOprType.DROP)
        self._table_refs = table_refs
        self._table_ids = table_ids
        self._if_exists = if_exists

    @property
    def table_refs(self):
        return self._table_refs

    @property
    def table_ids(self):
        return self._table_ids

    @property
    def if_exists(self):
        return self._if_exists

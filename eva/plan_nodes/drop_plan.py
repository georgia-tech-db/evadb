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

from eva.parser.table_ref import TableInfo
from eva.plan_nodes.abstract_plan import AbstractPlan
from eva.plan_nodes.types import PlanOprType


class DropPlan(AbstractPlan):
    """
    This plan is used for storing information required for drop table
    operations.
    Arguments:
        table_ref {TableRef} -- table ref for table to be truncated in storage
        if_exists {bool} -- if True do not throw error if table does not exist
    """

    def __init__(self, table_infos: List[TableInfo], if_exists: bool):
        super().__init__(PlanOprType.DROP)
        self._table_infos = table_infos
        self._if_exists = if_exists

    @property
    def table_infos(self):
        return self._table_infos

    @property
    def if_exists(self):
        return self._if_exists

    def __str__(self):
        return "DropPlan(_table_infos={}, if_exists={})".format(
            self._table_infos, self._if_exists
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), tuple(self._table_infos), self.if_exists))

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
from eva.parser.table_ref import TableInfo, TableRef
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


# Modified
class RenamePlan(AbstractPlan):
    """
    This plan is used for storing information required for rename table
    operations.
    Arguments:
        old_table {TableRef} -- table ref for table to be renamed in storage
        new_name {TableInfo} -- new name of old_table
    """

    def __init__(self, old_table: TableRef, new_name: TableInfo):
        super().__init__(PlanOprType.RENAME)
        self._old_table = old_table
        self._new_name = new_name

    @property
    def old_table(self):
        return self._old_table

    @property
    def new_name(self):
        return self._new_name

    def __str__(self):
        return "RenamePlan(old_table={}, \
            new_name={})".format(
            self._old_table, self._new_name
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.old_table, self.new_name))

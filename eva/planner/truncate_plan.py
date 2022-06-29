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

from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType
from eva.parser.table_ref import TableRef


class TruncatePlan(AbstractPlan):
    """
    This plan is used for storing information required for truncate table
    operations.
    Arguments:
        table_ref {TableRef} -- table ref for table to be truncated in storage
        table_id {int} -- catalog table id for the table
    """

    def __init__(self, table_ref: TableRef,
                 table_id: int):
        super().__init__(PlanOprType.TRUNCATE)
        self._table_ref = table_ref
        self._table_id = table_id

    @property
    def table_ref(self):
        return self._table_ref

    @property
    def table_id(self):
        return self._table_id

    # @property
    # def if_not_exists(self):
    #     return self._if_not_exists

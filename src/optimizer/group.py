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

from src.optimizer.operators import Operator
from src.utils.logging_manager import LoggingManager, LoggingLevel
from typing import List


INVALID_GROUP_ID = -1


class Group:

    def __init__(self, group_id: int):
        self._group_id = group_id
        self._logical_exprs = []
        self._physical_exprs = []

    @property
    def group_id(self):
        return self._group_id

    def get_logical_expr(self):
        return self._logical_exprs[0]
    
    def add_expr(self, expr: 'GroupExpression'):
        if expr.group_id == INVALID_GROUP_ID:
            expr.group_id = self.group_id

        if expr.group_id != self.group_id:
            LoggingManager().log('Expected group id {}, found {}'.format(
                self.group_id, expr.group_id))
            return

        if expr.opr.is_logical():
            self._add_logical_expr(expr)
        else:
            self._add_physical_expr(expr)

    def erase_grp(self):
        self._logical_exprs.clear()
        self._physical_exprs.clear()
    
    def _add_logical_expr(self, expr: 'GroupExpression'):
        self._logical_exprs.append(expr)

    def _add_physical_expr(self, expr: 'GroupExpression'):
        self._physical_exprs.append(expr)

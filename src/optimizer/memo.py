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

from src.optimizer.group_expression import GroupExpression
from src.optimizer.group import Group
from src.utils.logging_manager import LoggingManager, LoggingLevel


class Memo:
    def __init__(self):
        self._group_exprs = dict()
        self._groups = []

    def _create_new_group(self, expr: GroupExpression):
        self._groups.append([expr])

    def add_group_expr(self, expr: GroupExpression):
        # existing expression
        if expr in self._group_exprs:
            expr.group_id = self._group_exprs[expr]
            return

        # new expression
        # existing group
        if expr.group_id != Group.default_id:
            if expr.group_id < len(self._groups):
                self._groups[expr.group_id].add_expr(expr)
                self._group_exprs[expr] = expr.group_id
            else:
                LoggingManager().log('Group Id out of bound', LoggingLevel.ERROR)

        # create a new group
        expr.group_id = len(self._groups)
        self._groups.append(Group(expr.group_id))
        self._groups[expr.group_id].add_expr(expr)
        self._group_exprs[expr] = expr.group_id

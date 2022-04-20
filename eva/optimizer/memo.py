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

from eva.optimizer.group_expression import GroupExpression
from eva.optimizer.group import Group
from eva.utils.logging_manager import LoggingLevel, LoggingManager
from eva.constants import UNDEFINED_GROUP_ID


class Memo:
    """
    For now, we assume every group has only one logic expression.
    """

    def __init__(self):
        # self map to speed up finding duplicates
        self._group_exprs = dict()
        self._groups = dict()

    @property
    def groups(self):
        return self._groups

    @property
    def group_exprs(self):
        return self._group_exprs

    def find_duplicate_expr(self, expr: GroupExpression) -> GroupExpression:
        if expr in self.group_exprs:
            return self.group_exprs[expr]
        else:
            return None

    def get_group_by_id(self, group_id: int) -> GroupExpression:
        if group_id in self._groups.keys():
            return self._groups[group_id]
        else:
            LoggingManager().log('Missing group id', LoggingLevel.ERROR)

    def get_group_by_id(self, group_id: int) -> GroupExpression:
        if group_id in self._groups.keys():
            return self._groups[group_id]
        else:
            LoggingManager().log('Missing group id', LoggingLevel.ERROR)

    """
    For the consistency of the memo, all modification should use the
    following functions.
    """

    def _create_new_group(self, expr: GroupExpression):
        """
        Create new group for the expr
        """
        new_group_id = len(self._groups)
        self._groups[new_group_id] = Group(new_group_id)
        self._insert_expr(expr, new_group_id)

    def _insert_expr(self, expr: GroupExpression, group_id: int):
        """
        Insert a group expressoin into a particular group
        """
        assert group_id < len(self.groups), 'Group Id out of the bound'

        group = self.groups[group_id]
        group.add_expr(expr)
        self._group_exprs[expr] = expr

    def erase_group(self, group_id: int):
        """
        Remove all the expr from the group_id
        """
        group = self.groups[group_id]
        for expr in group.logical_exprs:
            print(expr)
            del self._group_exprs[expr]
        for expr in group.physical_exprs:
            del self._group_exprs[expr]

        group.clear_grp_exprs()

    def add_group_expr(self,
                       expr: GroupExpression,
                       group_id: int = UNDEFINED_GROUP_ID) -> GroupExpression:
        """
        Add an expression into the memo.
        If expr exists, we return it.
        If group_id is not specified, creates a new group
        Otherwise, inserts the expr into specified group.
        """
        # check duplicate expression
        duplicate_expr = self.find_duplicate_expr(expr)
        if duplicate_expr is not None:
            return duplicate_expr

        # did not find a dulpicate expression
        expr.group_id = group_id

        if expr.group_id == UNDEFINED_GROUP_ID:
            self._create_new_group(expr)
        else:
            self._insert_expr(expr, group_id)

        assert expr.group_id is not UNDEFINED_GROUP_ID, '''Expr
                                                        should have a
                                                        valid group
                                                        id'''
        return expr

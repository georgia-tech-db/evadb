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
from eva.optimizer.group import Group, INVALID_GROUP_ID
from eva.utils.logging_manager import LoggingLevel, LoggingManager


class Memo:
    """
    For now, we assume every group has only one logic expression.
    """

    def __init__(self):
        self._group_exprs = dict()
        self._groups = {}

    @property
    def groups(self):
        return self._groups

    @property
    def group_exprs(self):
        return self._group_exprs

    def get_group_id(self, expr: GroupExpression) -> int:
        """
        Find whether expr is in any exising group.
        """
        if expr in self.group_exprs:
            return self.group_exprs[expr]
        else:
            return INVALID_GROUP_ID

    def get_group_by_id(self, group_id: int) -> GroupExpression:
        if group_id in self._groups.keys():
            return self._groups[group_id]
        else:
            LoggingManager().log('Missing group id', LoggingLevel.ERROR)

    """
    For the consistency of the memo, all modification should use the
    following functions.
    """

    def _append_expr(self, expr: GroupExpression):
        """
        Append the expr into a new group, and update the group_id of expr
        """
        expr.group_id = len(self._groups)
        self._groups.append(Group(expr.group_id))
        self.groups[expr.group_id].add_expr(expr)
        self._group_exprs[expr] = expr.group_id

    def _insert_expr(self, expr: GroupExpression, group_id: int):
        """
        Insert a group expressoin into a particular group, update the
        group_id of expr
        """
        assert expr.group_id == INVALID_GROUP_ID, \
            'Expression: %s is already in the memo' % expr
        assert group_id < len(self.groups), 'Group Id out of the bound'

        group = self.groups[group_id]
        assert len(group.logical_exprs) == 0, \
            'Expression exists in the targeted inserted group. Details: %s' \
            % group.logical_exprs

        self.groups[group_id].add_expr(expr)
        self._group_exprs[expr] = group_id
        expr.group_id = group_id

    def _remove_expr(self, expr: GroupExpression):
        """
        Remove the expr from the memo, and update the group_id of expr
        to be INVALID_GROUP_ID.
        """
        group_id = self.get_group_id(expr)
        assert group_id == expr.group_id, \
            'Inconsistent memo found when removing expression: %s' % expr

        if group_id == INVALID_GROUP_ID:
            return

        del self._group_exprs[expr]
        self.groups[group_id].clear_grp_exprs()
        expr.group_id = INVALID_GROUP_ID

    def add_group_expr(self, expr: GroupExpression) -> GroupExpression:
        """
        Add an expression into the memo.
        If expr.group_id is not set, we will try reuse the exsiting one
        (i.e., for rule_explored).
        Otherwise, the expr will be considered as a new expression and
        inserted into targeted group.
        """
        # If not forcing a group id
        if expr.group_id == INVALID_GROUP_ID:
            group_id = self.get_group_id(expr)
            if group_id != INVALID_GROUP_ID:
                # we found exsiting one
                return self.groups[group_id].logical_exprs[0]
            else:
                # we append the expr as new one
                self._append_expr(expr)
                return expr
        # If forcing a group id
        else:
            group_id = expr.group_id
            assert group_id < len(self.groups), 'Group Id out of the bound'
            assert len(self.groups[group_id].logical_exprs) < 2, \
                'Unexpected number of expressions: %s' \
                % self.groups[group_id].logical_exprs
            if len(self.groups[group_id].logical_exprs) == 1:
                old_expr = self.groups[group_id].logical_exprs[0]
                self._remove_expr(old_expr)

            expr.group_id = INVALID_GROUP_ID
            self._insert_expr(expr, group_id)
            return expr

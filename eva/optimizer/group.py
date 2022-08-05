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
from __future__ import annotations

from typing import Dict, List

from eva.constants import UNDEFINED_GROUP_ID
from eva.optimizer.group_expression import GroupExpression
from eva.optimizer.property import Property
from eva.utils.logging_manager import logger


class Winner:
    def __init__(self, grp_expr: GroupExpression, cost: float):
        self._cost = cost
        self._grp_expr = grp_expr

    @property
    def cost(self):
        return self._cost

    @property
    def grp_expr(self):
        return self._grp_expr


class Group:
    def __init__(self, group_id: int, aliases: List[str] = None):
        self._group_id = group_id
        self._aliases = aliases
        self._logical_exprs = []
        self._physical_exprs = []
        self._winner_exprs: Dict[Property, Winner] = {}
        self._is_explored = False

    @property
    def group_id(self):
        return self._group_id

    @property
    def aliases(self):
        return self._aliases

    @property
    def logical_exprs(self):
        return self._logical_exprs

    @property
    def physical_exprs(self):
        return self._physical_exprs

    def is_explored(self):
        return self._is_explored

    def mark_explored(self):
        self._is_explored = True

    def __str__(self) -> str:
        return "%s(%s)" % (
            type(self).__name__,
            ", ".join("%s=%s" % item for item in vars(self).items()),
        )

    def add_expr(self, expr: GroupExpression):
        if expr.group_id == UNDEFINED_GROUP_ID:
            expr.group_id = self.group_id

        if expr.group_id != self.group_id:
            logger.error(
                "Expected group id {}, found {}".format(self.group_id, expr.group_id)
            )
            return

        if expr.opr.is_logical():
            self._add_logical_expr(expr)
        else:
            self._add_physical_expr(expr)

    def get_best_expr(self, property: Property) -> GroupExpression:
        winner = self._winner_exprs.get(property, None)
        if winner:
            return winner.grp_expr
        else:
            return None

    def get_best_expr_cost(self, property: Property):
        winner = self._winner_exprs.get(property, None)
        if winner:
            return winner.cost
        else:
            return None

    def add_expr_cost(self, expr: GroupExpression, property, cost):
        existing_winner = self._winner_exprs.get(property, None)
        if not existing_winner or existing_winner.cost > cost:
            self._winner_exprs[property] = Winner(expr, cost)

    def clear_grp_exprs(self):
        self._logical_exprs.clear()
        self._physical_exprs.clear()

    def _add_logical_expr(self, expr: GroupExpression):
        self._logical_exprs.append(expr)

    def _add_physical_expr(self, expr: GroupExpression):
        self._physical_exprs.append(expr)

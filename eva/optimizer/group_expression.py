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

from eva.constants import UNDEFINED_GROUP_ID
from eva.optimizer.operators import Operator
from eva.optimizer.rules.rules_base import RuleType


class GroupExpression:
    def __init__(
        self,
        opr: Operator,
        group_id: int = UNDEFINED_GROUP_ID,
        children: List[int] = [],
    ):
        # remove this assert after fixing
        # optimizer_context:_xform_opr_to_group_expr
        assert (
            len(opr.children) == 0
        ), """Cannot create a group expression
                                from operator with children"""
        self._opr = opr
        self._group_id = group_id
        self._children = children
        self._rules_explored = RuleType.INVALID_RULE

    @property
    def opr(self):
        return self._opr

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, new_id):
        self._group_id = new_id

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, new_children):
        self._children = new_children

    def append_child(self, child_id: int):
        self._children.append(child_id)

    @property
    def rules_explored(self):
        return self._rules_explored

    def is_logical(self):
        return self.opr.is_logical()

    def mark_rule_explored(self, rule_id: RuleType):
        self._rules_explored |= rule_id

    def is_rule_explored(self, rule_id: RuleType):
        return (self._rules_explored & rule_id) == rule_id

    def __eq__(self, other: "GroupExpression"):
        return (
            self.group_id == other.group_id
            and self.opr == other.opr
            and self.children == other.children
        )

    def __str__(self) -> str:
        return "%s(%s)" % (
            type(self).__name__,
            ", ".join("%s=%s" % item for item in vars(self).items()),
        )

    def __hash__(self):
        return hash((self.opr, tuple(self.children)))

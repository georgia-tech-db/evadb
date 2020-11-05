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
from src.optimizer.group import INVALID_GROUP_ID
from typing import List


class GroupExpression:
    def __init__(self,
                 opr: Operator,
                 group_id: int = INVALID_GROUP_ID,
                 children: List[int] = []):
        self._opr = opr
        self._group_id = group_id
        self._children = children
        self._rules_explored = 0

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

    def append_child(self, child_id: int):
        self._children.append(child_id)

    @property
    def rules_explored(self):
        return self._rules_explored

    def mark_rule_explored(self, rule_id: int):
        self._rules_explored |= rule_id

    def is_rule_explored(self, rule_id: int):
        return self._rules_explored & rule_id

    def __eq__(self, other: 'GroupExpression'):
        return (self.opr == other.opr and
                self.children == other.children)

    def __str__(self) -> str:
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    def __hash__(self):
        # correct this hash function.
        # we are taking hash of just the opr type

        curr_hash = id(self.opr)
        for child_id in self.children:
            curr_hash ^= hash(child_id)
        return curr_hash

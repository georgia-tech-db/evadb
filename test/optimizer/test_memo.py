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
import unittest

from mock import MagicMock

from eva.constants import UNDEFINED_GROUP_ID
from eva.optimizer.memo import Memo


class MemoTest(unittest.TestCase):
    def test_memo_add_with_no_id(self):
        group_expr = MagicMock()
        group_expr.group_id = UNDEFINED_GROUP_ID
        memo = Memo()
        memo.add_group_expr(group_expr)
        self.assertEqual(0, group_expr.group_id)

    def test_memo_add_with_forcing_id(self):
        group_expr = MagicMock()
        group_expr.group_id = 0
        memo = Memo()
        self.assertEqual(memo.add_group_expr(group_expr), group_expr)
        self.assertEqual(len(memo.groups), 1)

    def test_memo_add_under_existing_group(self):
        group_expr1 = MagicMock()
        group_expr1.group_id = UNDEFINED_GROUP_ID
        group_expr2 = MagicMock()
        group_expr2.group_id = 0

        memo = Memo()
        expr = memo.add_group_expr(group_expr1)
        ret_expr = memo.add_group_expr(group_expr2)
        self.assertEqual(expr.group_id, 0)
        self.assertEqual(ret_expr.group_id, 1)
        self.assertEqual(len(memo.groups), 2)
        self.assertEqual(len(memo.group_exprs), 2)

        memo = Memo()
        memo.add_group_expr(group_expr2)
        expr = memo.add_group_expr(group_expr1)
        self.assertEqual(expr.group_id, 1)
        self.assertEqual(len(memo.groups), 2)
        self.assertEqual(len(memo.group_exprs), 2)
